from __future__ import annotations

from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.config import Settings, load_settings
from app.db.sqlite import SqliteDatabase
from app.handlers.content import send_post_demo
from app.localization.locales import t
from app.localization.strings import STR

router = Router(name="callbacks")


@router.callback_query(F.data == "menu:commands")
async def menu_commands(cb: CallbackQuery, lang: str = "en") -> None:
    if not cb.message:
        await cb.answer()
        return
    await cb.answer()
    await cb.message.answer(t("HELP_COMMANDS", lang), disable_web_page_preview=True)


@router.callback_query(F.data == "menu:demo_post")
async def menu_demo_post(cb: CallbackQuery, lang: str = "en") -> None:
    if not cb.message:
        await cb.answer()
        return
    await cb.answer()
    await send_post_demo(cb.message, lang=lang)


@router.callback_query(F.data == "menu:templates")
async def menu_templates(cb: CallbackQuery, lang: str = "en") -> None:
    if not cb.message:
        await cb.answer()
        return
    await cb.answer()
    await cb.message.answer(t("HELP_TEMPLATE_MGMT", lang), disable_web_page_preview=True)


@router.callback_query(F.data.startswith("cta:"))
async def cta_click(cb: CallbackQuery) -> None:
    """
    Logs CTA performance and then replies with the actual link.
    URL buttons don't trigger callbacks, so we use callback -> send link.
    """
    if not cb.from_user:
        return

    button_id = (cb.data or "cta:unknown").split(":", 1)[1]
    settings: Settings = load_settings()

    # Log click (best-effort)
    try:
        db = SqliteDatabase(settings.db_url)
        await db.connect()
        await db.init_schema()
        await db.log_button_click(
            uid=cb.from_user.id,
            button_id=button_id,
            chat_id=cb.message.chat.id if cb.message else None,
            message_id=cb.message.message_id if cb.message else None,
            created_at=datetime.now(tz=timezone.utc),
            payload=None,
        )
        await db.close()
    except Exception:
        # Never block the UX because of analytics
        pass

    # UX: answer callback quickly + send the actual link
    await cb.answer("Noted boss ✅", show_alert=False)

    if button_id == "leave_comment":
        await cb.message.answer(f"{STR.BTN_GET_LINK}\n{settings.comment_url}", disable_web_page_preview=True)
        return

    await cb.message.answer(f"{STR.BTN_GET_LINK}\n{settings.conversion_url}", disable_web_page_preview=True)

