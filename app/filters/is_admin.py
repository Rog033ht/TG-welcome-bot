from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.config import Settings, load_settings


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        settings: Settings = load_settings()
        if not message.from_user:
            return False
        return message.from_user.id in settings.admin_id_set

