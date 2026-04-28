from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.localization.strings import STR


def main_menu_kb(
    *,
    groups_url: str,
    app_url: str,
    official_bot_url: str,
    support_url: str,
) -> InlineKeyboardMarkup:
    # UI vibe: emoji + clear CTA links (matches screenshot style)
    rows = [
        [InlineKeyboardButton(text=STR.BTN_GROUPS, url=groups_url)],
        [InlineKeyboardButton(text=STR.BTN_APP, url=app_url)],
        [InlineKeyboardButton(text=STR.BTN_OFFICIAL_BOT, url=official_bot_url)],
        [InlineKeyboardButton(text=STR.BTN_SUPPORT, url=support_url)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

