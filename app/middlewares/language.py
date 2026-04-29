from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.localization.locales import normalize_lang


class LanguageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        event_user = data.get("event_from_user")
        lang_code = getattr(event_user, "language_code", None)
        data["lang"] = normalize_lang(lang_code)
        return await handler(event, data)

