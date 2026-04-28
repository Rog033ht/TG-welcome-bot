from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.localization.strings import STR

router = Router(name="spin")


@router.message(Command("spin"))
async def spin_cmd(message: Message) -> None:
    await message.answer(f"<b>{STR.SPIN_TITLE}</b>\n\n{STR.SPIN_SOON}")

