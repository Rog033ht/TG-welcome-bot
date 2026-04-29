from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.db.base import Database, UserUpsert
from app.config import load_settings
from app.keyboards import main_menu_kb
from app.localization.strings import STR
from app.services.followups import FollowupService
from datetime import datetime, timezone

router = Router(name="start")


@router.message(CommandStart())
async def start_cmd(message: Message, followups: FollowupService, db: Database) -> None:
    settings = load_settings()

    # Template A (instant)
    await message.answer(STR.WELCOME_A, disable_web_page_preview=True)

    # Schedule Template B (after 5 minutes)
    if message.from_user:
        # Fail-safe: ensure user row exists before enqueueing FK-bound followup.
        u = message.from_user
        await db.upsert_user(
            UserUpsert(
                uid=u.id,
                username=u.username,
                full_name=u.full_name,
                join_date=datetime.now(tz=timezone.utc),
            )
        )
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

