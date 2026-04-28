from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.config import load_settings
from app.keyboards import main_menu_kb
from app.localization.strings import STR
from app.services.followups import FollowupService

router = Router(name="start")


@router.message(CommandStart())
async def start_cmd(message: Message) -> None:
    settings = load_settings()
    followups: FollowupService | None = message.bot.get("followups") if message.bot else None

    # Template A (instant)
    await message.answer(STR.WELCOME_A, disable_web_page_preview=True)

    # Schedule Template B (after 5 minutes)
    if followups and message.from_user:
        await followups.enqueue_template_b(uid=message.from_user.id)

    text = f"{STR.WELCOME_TITLE}\n\n{STR.WELCOME_SUB}"
    await message.answer(
        text,
        reply_markup=main_menu_kb(
            groups_url=settings.groups_url,
            app_url=settings.app_url,
            official_bot_url=settings.official_bot_url,
            support_url=settings.support_url,
        ),
        disable_web_page_preview=True,
    )

