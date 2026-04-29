from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards import main_menu_kb
from app.localization.locales import t

router = Router(name="start")


# ignore_mention: in private chat, users often paste /start@OldBot after a token/username
# change; strict mention matching would drop the update with no reply.
@router.message(CommandStart(ignore_mention=True))
async def start_cmd(message: Message, lang: str = "en") -> None:
    text = f"{t('WELCOME_TITLE', lang)}\n\n{t('WELCOME_SUB', lang)}"
    await message.answer(
        text,
        reply_markup=main_menu_kb(lang=lang),
        disable_web_page_preview=True,
    )

