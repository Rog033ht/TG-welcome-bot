from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Optional

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter, TelegramServerError
from loguru import logger

from app.config import Settings
from app.db.base import Database
from app.utils.anti_spam import append_unique_suffix


BroadcastStatus = Literal["running", "paused", "done", "error"]


@dataclass
class BroadcastJob:
    id: int
    asset_name: str
    caption: str
    status: BroadcastStatus
    last_uid: int
    sent_count: int
    fail_count: int


class BroadcastService:
    def __init__(self, *, db: Database, settings: Settings) -> None:
        self._db = db
        self._settings = settings
        self._lock = asyncio.Lock()
        self._active_task: Optional[asyncio.Task] = None
        self._paused_ids: set[int] = set()

    def is_running(self) -> bool:
        return self._active_task is not None and not self._active_task.done()

    async def pause(self, broadcast_id: int) -> None:
        self._paused_ids.add(broadcast_id)
        job = await self._db.get_broadcast(broadcast_id=broadcast_id)
        if job:
            await self._db.update_broadcast_progress(
                broadcast_id=broadcast_id,
                status="paused",
                last_uid=int(job["last_uid"]),
                sent_count=int(job["sent_count"]),
                fail_count=int(job["fail_count"]),
                updated_at=datetime.now(tz=timezone.utc),
            )

    async def start_or_resume(self, *, bot: Bot, broadcast_id: int) -> None:
        async with self._lock:
            if self.is_running():
                return
            self._active_task = asyncio.create_task(self._run_job(bot=bot, broadcast_id=broadcast_id))

    async def _run_job(self, *, bot: Bot, broadcast_id: int) -> None:
        logger.info(f"Broadcast job start id={broadcast_id}")
        try:
            asset = None
            job_dict = await self._db.get_broadcast(broadcast_id=broadcast_id)
            if not job_dict:
                return

            job = BroadcastJob(**job_dict)  # type: ignore[arg-type]
            asset = await self._db.get_asset(name=job.asset_name)
            if not asset:
                await self._db.update_broadcast_progress(
                    broadcast_id=broadcast_id,
                    status="error",
                    last_uid=job.last_uid,
                    sent_count=job.sent_count,
                    fail_count=job.fail_count,
                    updated_at=datetime.now(tz=timezone.utc),
                )
                return

            rps = max(1, int(self._settings.broadcast_rps))
            delay = 1.0 / float(rps)

            status: BroadcastStatus = "running"
            last_uid = int(job.last_uid)
            sent = int(job.sent_count)
            failed = int(job.fail_count)

            while True:
                if broadcast_id in self._paused_ids:
                    status = "paused"
                    break

                uids = await self._db.list_users_after(after_uid=last_uid, limit=500)
                if not uids:
                    status = "done"
                    break

                for uid in uids:
                    if broadcast_id in self._paused_ids:
                        status = "paused"
                        break

                    ok = await self._send_one(bot=bot, uid=uid, asset=asset, caption=job.caption)
                    last_uid = uid
                    if ok:
                        sent += 1
                    else:
                        failed += 1

                    await self._db.update_broadcast_progress(
                        broadcast_id=broadcast_id,
                        status="running",
                        last_uid=last_uid,
                        sent_count=sent,
                        fail_count=failed,
                        updated_at=datetime.now(tz=timezone.utc),
                    )

                    await asyncio.sleep(delay)

                if status == "paused":
                    break

            await self._db.update_broadcast_progress(
                broadcast_id=broadcast_id,
                status=status,
                last_uid=last_uid,
                sent_count=sent,
                fail_count=failed,
                updated_at=datetime.now(tz=timezone.utc),
            )
        except Exception:
            logger.exception(f"Broadcast job crashed id={broadcast_id}")
            try:
                job = await self._db.get_broadcast(broadcast_id=broadcast_id)
                if job:
                    await self._db.update_broadcast_progress(
                        broadcast_id=broadcast_id,
                        status="error",
                        last_uid=int(job["last_uid"]),
                        sent_count=int(job["sent_count"]),
                        fail_count=int(job["fail_count"]),
                        updated_at=datetime.now(tz=timezone.utc),
                    )
            except Exception:
                pass
        finally:
            self._paused_ids.discard(broadcast_id)
            logger.info(f"Broadcast job stop id={broadcast_id}")

    async def _send_one(self, *, bot: Bot, uid: int, asset: dict, caption: str) -> bool:
        cap = append_unique_suffix(
            caption,
            enabled=self._settings.broadcast_unique_suffix,
            add_timestamp=True,
        )

        # Minimal CTA: keep existing callback tracking in future via reply_markup at send-time
        try:
            ftype = asset["file_type"]
            fid = asset["file_id"]
            if ftype == "photo":
                await bot.send_photo(uid, photo=fid, caption=cap)
            elif ftype == "video":
                await bot.send_video(uid, video=fid, caption=cap)
            else:
                await bot.send_message(uid, cap, disable_web_page_preview=True)
            return True
        except TelegramRetryAfter as e:
            await asyncio.sleep(float(getattr(e, "retry_after", 1)))
            return False
        except (TelegramForbiddenError, TelegramServerError):
            return False
        except Exception:
            return False

