from __future__ import annotations

from datetime import datetime
from urllib.parse import urlparse

import aiosqlite

from app.db.base import Database, UserUpsert


class SqliteDatabase(Database):
    def __init__(self, db_url: str) -> None:
        self._db_url = db_url
        self._conn: aiosqlite.Connection | None = None

    def _path_from_url(self) -> str:
        parsed = urlparse(self._db_url)
        # Expected: sqlite+aiosqlite:///./data/bot.sqlite3 or sqlite+aiosqlite:////abs/path
        if not parsed.scheme.startswith("sqlite"):
            raise ValueError(f"Unsupported DB_URL scheme: {parsed.scheme}")
        path = parsed.path
        if path.startswith("/") and len(path) >= 2 and path[1] == ".":
            # '/./data/...' -> './data/...'
            return path[1:]
        if path.startswith("/") and parsed.netloc == "":
            # absolute path (e.g. '/Users/.../bot.sqlite3')
            return path
        return path.lstrip("/")

    async def connect(self) -> None:
        if self._conn:
            return
        path = self._path_from_url()
        self._conn = await aiosqlite.connect(path)
        await self._conn.execute("PRAGMA journal_mode=WAL;")
        await self._conn.execute("PRAGMA foreign_keys=ON;")
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
        self._conn = None

    async def init_schema(self) -> None:
        assert self._conn is not None
        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              uid INTEGER PRIMARY KEY,
              username TEXT,
              full_name TEXT NOT NULL,
              join_date TEXT NOT NULL
            );
            """
        )

        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS button_clicks (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              uid INTEGER NOT NULL,
              button_id TEXT NOT NULL,
              payload TEXT,
              chat_id INTEGER,
              message_id INTEGER,
              created_at TEXT NOT NULL,
              FOREIGN KEY(uid) REFERENCES users(uid) ON DELETE CASCADE
            );
            """
        )
        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS followups (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              uid INTEGER NOT NULL,
              template TEXT NOT NULL,
              due_at TEXT NOT NULL,
              sent_at TEXT,
              created_at TEXT NOT NULL,
              FOREIGN KEY(uid) REFERENCES users(uid) ON DELETE CASCADE
            );
            """
        )
        await self._conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_followups_due
            ON followups (sent_at, due_at);
            """
        )

        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS media_assets (
              name TEXT PRIMARY KEY,
              file_id TEXT NOT NULL,
              file_type TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            """
        )
        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS broadcasts (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              asset_name TEXT NOT NULL,
              caption TEXT NOT NULL,
              status TEXT NOT NULL,
              last_uid INTEGER NOT NULL DEFAULT 0,
              sent_count INTEGER NOT NULL DEFAULT 0,
              fail_count INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              FOREIGN KEY(asset_name) REFERENCES media_assets(name) ON DELETE RESTRICT
            );
            """
        )
        await self._conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_broadcasts_status
            ON broadcasts (status);
            """
        )
        await self._conn.commit()

    async def upsert_user(self, user: UserUpsert) -> None:
        assert self._conn is not None
        await self._conn.execute(
            """
            INSERT INTO users (uid, username, full_name, join_date)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(uid) DO UPDATE SET
              username=excluded.username,
              full_name=excluded.full_name
            """,
            (
                user.uid,
                user.username,
                user.full_name,
                user.join_date.isoformat(timespec="seconds"),
            ),
        )
        await self._conn.commit()

    async def log_button_click(
        self,
        *,
        uid: int,
        button_id: str,
        chat_id: int | None,
        message_id: int | None,
        created_at: datetime,
        payload: str | None = None,
    ) -> None:
        assert self._conn is not None
        await self._conn.execute(
            """
            INSERT INTO button_clicks (uid, button_id, payload, chat_id, message_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                uid,
                button_id,
                payload,
                chat_id,
                message_id,
                created_at.isoformat(timespec="seconds"),
            ),
        )
        await self._conn.commit()

    async def enqueue_followup(
        self,
        *,
        uid: int,
        template: str,
        due_at: datetime,
        created_at: datetime,
    ) -> bool:
        """
        Idempotent-ish enqueue:
        - only one pending followup per (uid, template) at a time.
        """
        assert self._conn is not None
        cur = await self._conn.execute(
            """
            SELECT id FROM followups
            WHERE uid = ? AND template = ? AND sent_at IS NULL
            LIMIT 1
            """,
            (uid, template),
        )
        row = await cur.fetchone()
        await cur.close()
        if row:
            return False

        await self._conn.execute(
            """
            INSERT INTO followups (uid, template, due_at, sent_at, created_at)
            VALUES (?, ?, ?, NULL, ?)
            """,
            (
                uid,
                template,
                due_at.isoformat(timespec="seconds"),
                created_at.isoformat(timespec="seconds"),
            ),
        )
        await self._conn.commit()
        return True

    async def fetch_due_followups(
        self,
        *,
        now: datetime,
        limit: int = 100,
    ) -> list[dict]:
        assert self._conn is not None
        cur = await self._conn.execute(
            """
            SELECT id, uid, template
            FROM followups
            WHERE sent_at IS NULL AND due_at <= ?
            ORDER BY due_at ASC
            LIMIT ?
            """,
            (now.isoformat(timespec="seconds"), limit),
        )
        rows = await cur.fetchall()
        await cur.close()
        return [{"id": r[0], "uid": r[1], "template": r[2]} for r in rows]

    async def mark_followup_sent(self, *, followup_id: int, sent_at: datetime) -> None:
        assert self._conn is not None
        await self._conn.execute(
            """
            UPDATE followups
            SET sent_at = ?
            WHERE id = ?
            """,
            (sent_at.isoformat(timespec="seconds"), followup_id),
        )
        await self._conn.commit()

    async def save_asset(
        self,
        *,
        name: str,
        file_id: str,
        file_type: str,
        created_at: datetime,
    ) -> None:
        assert self._conn is not None
        await self._conn.execute(
            """
            INSERT INTO media_assets (name, file_id, file_type, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
              file_id=excluded.file_id,
              file_type=excluded.file_type
            """,
            (name, file_id, file_type, created_at.isoformat(timespec="seconds")),
        )
        await self._conn.commit()

    async def get_asset(self, *, name: str) -> dict | None:
        assert self._conn is not None
        cur = await self._conn.execute(
            """
            SELECT name, file_id, file_type
            FROM media_assets
            WHERE name = ?
            """,
            (name,),
        )
        row = await cur.fetchone()
        await cur.close()
        if not row:
            return None
        return {"name": row[0], "file_id": row[1], "file_type": row[2]}

    async def create_broadcast(self, *, asset_name: str, caption: str, created_at: datetime) -> int:
        assert self._conn is not None
        now = created_at.isoformat(timespec="seconds")
        cur = await self._conn.execute(
            """
            INSERT INTO broadcasts (asset_name, caption, status, last_uid, sent_count, fail_count, created_at, updated_at)
            VALUES (?, ?, 'running', 0, 0, 0, ?, ?)
            """,
            (asset_name, caption, now, now),
        )
        await self._conn.commit()
        return int(cur.lastrowid)

    async def get_broadcast(self, *, broadcast_id: int) -> dict | None:
        assert self._conn is not None
        cur = await self._conn.execute(
            """
            SELECT id, asset_name, caption, status, last_uid, sent_count, fail_count
            FROM broadcasts
            WHERE id = ?
            """,
            (broadcast_id,),
        )
        row = await cur.fetchone()
        await cur.close()
        if not row:
            return None
        return {
            "id": row[0],
            "asset_name": row[1],
            "caption": row[2],
            "status": row[3],
            "last_uid": row[4],
            "sent_count": row[5],
            "fail_count": row[6],
        }

    async def update_broadcast_progress(
        self,
        *,
        broadcast_id: int,
        status: str,
        last_uid: int,
        sent_count: int,
        fail_count: int,
        updated_at: datetime,
    ) -> None:
        assert self._conn is not None
        await self._conn.execute(
            """
            UPDATE broadcasts
            SET status = ?,
                last_uid = ?,
                sent_count = ?,
                fail_count = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                status,
                last_uid,
                sent_count,
                fail_count,
                updated_at.isoformat(timespec="seconds"),
                broadcast_id,
            ),
        )
        await self._conn.commit()

    async def list_users_after(self, *, after_uid: int, limit: int) -> list[int]:
        assert self._conn is not None
        cur = await self._conn.execute(
            """
            SELECT uid
            FROM users
            WHERE uid > ?
            ORDER BY uid ASC
            LIMIT ?
            """,
            (after_uid, limit),
        )
        rows = await cur.fetchall()
        await cur.close()
        return [int(r[0]) for r in rows]

