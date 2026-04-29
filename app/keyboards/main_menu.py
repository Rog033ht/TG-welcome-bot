from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.localization.locales import t


def main_menu_kb(*, lang: str) -> InlineKeyboardMarkup:
    """Two-tap welcome: command list + demo post (callbacks, not URL flood)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("BTN_ALL_COMMANDS", lang),
                    callback_data="menu:commands",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t("BTN_DEMO_POST", lang),
                    callback_data="menu:demo_post",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t("BTN_TEMPLATE_MGMT", lang),
                    callback_data="menu:templates",
                ),
            ],
        ]
    )
