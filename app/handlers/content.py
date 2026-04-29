from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import load_settings
from app.keyboards import post_cta_kb
from app.localization.locales import t
from app.utils.anti_spam import append_unique_suffix

router = Router(name="content")


async def send_post_demo(message: Message, *, lang: str) -> None:
    """Sample post + CTA (used by /post_demo and main-menu callback)."""
    settings = load_settings()
    kb = post_cta_kb(lang=lang, button_id="leave_comment")
    caption = (
        "<b>🔥 Sample Clip</b>\n"
        "Solid 'to, boss. Check mo yung vibe.\n\n"
        "#PH #Taglish #Official\n\n"
        f"{t('POST_CTA', lang)}"
    )
    caption = append_unique_suffix(
        caption,
        enabled=settings.broadcast_unique_suffix,
        add_timestamp=True,
    )
    await message.answer(caption, reply_markup=kb, disable_web_page_preview=True)


@router.message(Command("post_demo", ignore_mention=True))
async def post_demo(message: Message, lang: str = "en") -> None:
    await send_post_demo(message, lang=lang)

