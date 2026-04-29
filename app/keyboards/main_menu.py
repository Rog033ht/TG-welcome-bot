from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.localization.locales import t


def main_menu_kb(
    *,
    lang: str,
    groups_url: str,
    app_url: str,
    official_bot_url: str,
    support_url: str,
) -> InlineKeyboardMarkup:
    # UI vibe: emoji + clear CTA links (matches screenshot style)
    rows = [
        [InlineKeyboardButton(text=t("BTN_GROUPS", lang), url=groups_url)],
        [InlineKeyboardButton(text=t("BTN_APP", lang), url=app_url)],
        [InlineKeyboardButton(text=t("BTN_OFFICIAL_BOT", lang), url=official_bot_url)],
        [InlineKeyboardButton(text=t("BTN_SUPPORT", lang), url=support_url)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

