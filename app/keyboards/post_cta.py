from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.localization.locales import t


def post_cta_kb(*, lang: str, button_id: str = "leave_comment") -> InlineKeyboardMarkup:
    # Callback (not URL) so we can track clicks reliably.
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("BTN_LEAVE_COMMENT", lang), callback_data=f"cta:{button_id}")],
        ]
    )

