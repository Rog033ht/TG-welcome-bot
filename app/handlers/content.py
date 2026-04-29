from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import load_settings
from app.keyboards import post_cta_kb
from app.localization.locales import t
from app.utils.anti_spam import append_unique_suffix

router = Router(name="content")


@router.message(Command("post_demo"))
async def post_demo(message: Message, lang: str = "en") -> None:
    # Placeholder for the future "Content Engine" broadcast system.
    # For now, we send a sample post vibe + "Leave a Comment".
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

