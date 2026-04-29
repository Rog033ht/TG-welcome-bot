from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User

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
        u: Optional[User] = None

        message: Optional[Message] = data.get("event_message")
        if message and message.from_user:
            u = message.from_user

        if u is None:
            callback: Optional[CallbackQuery] = data.get("event_callback_query")
            if callback and callback.from_user:
                u = callback.from_user

        if u is None:
            maybe_user = data.get("event_from_user")
            if isinstance(maybe_user, User):
                u = maybe_user

        if u:
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

