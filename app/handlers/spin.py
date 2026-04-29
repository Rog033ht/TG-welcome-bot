from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.localization.locales import t

router = Router(name="spin")


@router.message(Command("spin"))
async def spin_cmd(message: Message, lang: str = "en") -> None:
    await message.answer(f"<b>{t('SPIN_TITLE', lang)}</b>\n\n{t('SPIN_SOON', lang)}")

