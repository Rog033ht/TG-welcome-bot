from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from app.db.base import Database, UserUpsert


class UserTrackingMiddleware(BaseMiddleware):
    def __init__(self, *, db: Database) -> None:
        self._db = db

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        message: Optional[Message] = data.get("event_message")
        if message and message.from_user:
            u = message.from_user
            join_date = datetime.now(tz=timezone.utc)
            await self._db.upsert_user(
                UserUpsert(
                    uid=u.id,
                    username=u.username,
                    full_name=u.full_name,
                    join_date=join_date,
                )
            )

        return await handler(event, data)

