from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from loguru import logger

from app.config import Settings
from app.db.base import Database
from app.localization.strings import STR
from app.utils.anti_spam import append_unique_suffix


@dataclass(frozen=True)
class FollowupTemplates:
    TEMPLATE_B: str = "followup_b"


class FollowupService:
    def __init__(self, *, db: Database, settings: Settings) -> None:
        self._db = db
        self._settings = settings
        self._stop = asyncio.Event()

    async def stop(self) -> None:
        self._stop.set()

    async def enqueue_template_b(self, *, uid: int) -> bool:
        now = datetime.now(tz=timezone.utc)
        due = now + timedelta(minutes=5)
        return await self._db.enqueue_followup(
            uid=uid,
            template=FollowupTemplates.TEMPLATE_B,
            due_at=due,
            created_at=now,
        )

    async def run(self, bot: Bot) -> None:
        """
        Lightweight scheduler loop:
        - polls due followups from DB
        - sends messages
        - marks sent
        """
        logger.info("Followup scheduler started")
        try:
            while not self._stop.is_set():
                now = datetime.now(tz=timezone.utc)
                due = await self._db.fetch_due_followups(now=now, limit=100)
                for item in due:
                    await self._send_followup(bot=bot, followup_id=item["id"], uid=item["uid"], template=item["template"])
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    pass
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Followup scheduler crashed")
        finally:
            logger.info("Followup scheduler stopped")

    async def _send_followup(self, *, bot: Bot, followup_id: int, uid: int, template: str) -> None:
        now = datetime.now(tz=timezone.utc)
        if template == FollowupTemplates.TEMPLATE_B:
            msg = STR.FOLLOWUP_B.format(conversion_url=self._settings.conversion_url)
            msg = append_unique_suffix(msg, enabled=self._settings.broadcast_unique_suffix, add_timestamp=True)
            await bot.send_message(uid, msg, disable_web_page_preview=True)
            await self._db.mark_followup_sent(followup_id=followup_id, sent_at=now)
            return

        # Unknown template: mark as sent to avoid infinite loop
        await self._db.mark_followup_sent(followup_id=followup_id, sent_at=now)

