from __future__ import annotations

from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from app.db.sqlite import SqliteDatabase


router = Router(name="vote")


def _poll_id_from_start_text(text: str) -> str | None:
    # Deep-link format: /start vote_<poll_id>
    if not text:
        return None
    parts = text.strip().split()
    if not parts:
        return None
    last = parts[-1]
    if not last.startswith("vote_"):
        return None
    poll_id = last[len("vote_") :]
    if len(poll_id) != 8:
        return None
    return poll_id


@router.message(F.text.regexp(r"^/start\\s+vote_[0-9a-fA-F]{8}$"))
async def vote_start_handler(message: Message) -> None:
    poll_id = _poll_id_from_start_text(message.text or "")
    if not poll_id:
        return

    # Note: we store DB URL in Settings; easiest is to create a SqliteDatabase via load_settings.
    from app.config import load_settings

    settings = load_settings()
    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()
    result = await db.get_smart_poll_results(poll_id=poll_id)
    await db.close()

    if not result:
        await message.answer("Poll not found. It may be deleted or expired.")
        return

    # If there is an asset saved, show it as the poll cover (photo/video).
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"A: {result['option_a']} ({result['count_a']})",
                    callback_data=f"smartvote:{poll_id}:a",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"B: {result['option_b']} ({result['count_b']})",
                    callback_data=f"smartvote:{poll_id}:b",
                )
            ],
        ]
    )

    asset_name = result.get("asset_name")
    if asset_name:
        await db.connect()
        await db.init_schema()
        asset = await db.get_asset(name=asset_name)
        await db.close()
        if asset:
            try:
                if asset.get("file_type") == "photo":
                    await message.answer_photo(
                        photo=asset["file_id"],
                        caption=f"📊 {result['question']}",
                        reply_markup=kb,
                    )
                    return
                if asset.get("file_type") == "video":
                    await message.answer_video(
                        video=asset["file_id"],
                        caption=f"📊 {result['question']}",
                        reply_markup=kb,
                    )
                    return
            except Exception:
                # Fallback to text-only if sending media fails.
                pass

    await message.answer(
        f"📊 {result['question']}\n\nA: {result['option_a']} ({result['count_a']})\nB: {result['option_b']} ({result['count_b']})",
        reply_markup=kb,
    )


@router.callback_query(F.data.startswith("smartvote:"))
async def vote_callback(cb: CallbackQuery) -> None:
    if not cb.from_user:
        return

    if not (cb.data or "").startswith("smartvote:"):
        return

    parts = cb.data.split(":")
    # smartvote:<poll_id>:<a|b>
    if len(parts) != 3:
        await cb.answer()
        return

    poll_id = parts[1]
    option = parts[2].strip().lower()
    if option not in {"a", "b"}:
        await cb.answer()
        return

    from app.config import load_settings

    settings = load_settings()
    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()
    await db.upsert_smart_poll_vote(
        poll_id=poll_id,
        uid=cb.from_user.id,
        option=option,
        created_at=datetime.now(tz=timezone.utc),
    )
    result = await db.get_smart_poll_results(poll_id=poll_id)
    await db.close()

    if not result:
        await cb.answer("Vote saved ✅")
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"A: {result['option_a']} ({result['count_a']})",
                    callback_data=f"smartvote:{poll_id}:a",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"B: {result['option_b']} ({result['count_b']})",
                    callback_data=f"smartvote:{poll_id}:b",
                )
            ],
        ]
    )

    text = (
        f"📊 {result['question']}\n\n"
        f"A: {result['option_a']} ({result['count_a']})\n"
        f"B: {result['option_b']} ({result['count_b']})"
    )

    await cb.answer("Noted boss ✅", show_alert=False)

    # Try to edit in place; if it fails, fall back to sending a new message.
    try:
        if getattr(cb.message, "text", None) is not None:
            await cb.message.edit_text(text, reply_markup=kb)
        else:
            # For photo polls, editing caption is the safest.
            await cb.message.edit_caption(caption=text, reply_markup=kb)  # type: ignore[attr-defined]
    except Exception:
        await cb.message.answer(text, reply_markup=kb)

