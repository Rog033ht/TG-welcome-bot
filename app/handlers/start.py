from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.config import load_settings
from app.keyboards import main_menu_kb
from app.localization.locales import t

router = Router(name="start")


@router.message(CommandStart())
async def start_cmd(message: Message, lang: str = "en") -> None:
    settings = load_settings()

    text = f"{t('WELCOME_TITLE', lang)}\n\n{t('WELCOME_SUB', lang)}"
    await message.answer(
        text,
        reply_markup=main_menu_kb(
            lang=lang,
            groups_url=settings.groups_url,
            app_url=settings.app_url,
            official_bot_url=settings.official_bot_url,
            support_url=settings.support_url,
        ),
        disable_web_page_preview=True,
    )

