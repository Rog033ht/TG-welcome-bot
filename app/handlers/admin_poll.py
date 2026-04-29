from __future__ import annotations

from datetime import datetime, timezone, timedelta
from uuid import uuid4

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.config import load_settings
from app.db.sqlite import SqliteDatabase
from app.filters import IsAdmin


router = Router(name="admin_poll")
router.message.filter(IsAdmin())


class PollState(StatesGroup):
    asset_name = State()
    question = State()
    option_a = State()
    option_b = State()
    base_a = State()
    base_b = State()
    end_after_minutes = State()


@router.message(Command("poll_create", ignore_mention=True))
async def poll_create(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(PollState.asset_name)
    await message.answer(
        "<b>Smart Poll Builder</b>\n\n"
        "Step 1/7: Send asset name (saved via <code>/asset_save</code>) or type <code>skip</code>.\n"
        "Example: <code>poll_banner1</code>"
    )


@router.message(PollState.asset_name)
async def poll_asset(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if raw.lower() == "skip":
        await state.update_data(asset_name=None)
        await state.set_state(PollState.question)
        await message.answer(
            "Step 2/7: Send the poll question text.\n"
            "Example: <code>Which welcome offer do you prefer?</code>"
        )
        return

    settings = load_settings()
    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()
    asset = await db.get_asset(name=raw)
    await db.close()

    if not asset:
        await message.answer("Asset not found. Send another asset name or type <code>skip</code>.")
        return

    await state.update_data(asset_name=raw)
    await state.set_state(PollState.question)
    await message.answer(
        "Step 2/7: Send the poll question text.\n"
        "Example: <code>Which welcome offer do you prefer?</code>"
    )


@router.message(PollState.question)
async def poll_question(message: Message, state: FSMContext) -> None:
    q = (message.text or "").strip()
    if not q:
        await message.answer("Question cannot be empty. Please send the poll question text.")
        return
    await state.update_data(question=q)
    await state.set_state(PollState.option_a)
    await message.answer(
        "Step 3/7: Send <b>Option A</b> text.\n"
        "Example: <code>High bonus, higher rollover</code>"
    )


@router.message(PollState.option_a)
async def poll_option_a(message: Message, state: FSMContext) -> None:
    a = (message.text or "").strip()
    if not a:
        await message.answer("Option A cannot be empty. Please send the text.")
        return
    await state.update_data(option_a=a)
    await state.set_state(PollState.option_b)
    await message.answer(
        "Step 4/7: Send <b>Option B</b> text.\n"
        "Example: <code>Lower bonus, almost no rollover</code>"
    )


@router.message(PollState.option_b)
async def poll_option_b(message: Message, state: FSMContext) -> None:
    b = (message.text or "").strip()
    if not b:
        await message.answer("Option B cannot be empty. Please send the text.")
        return
    await state.update_data(option_b=b)
    await state.set_state(PollState.base_a)
    await message.answer(
        "Step 5/7: Send <b>base_a</b> (integer, starting votes for Option A).\n"
        "Example: <code>60</code>"
    )


def _parse_int(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


@router.message(PollState.base_a)
async def poll_base_a(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    n = _parse_int(raw)
    if n is None or n < 0:
        await message.answer("base_a must be a non-negative integer. Try again.")
        return
    await state.update_data(base_a=n)
    await state.set_state(PollState.base_b)
    await message.answer(
        "Step 6/7: Send <b>base_b</b> (integer, starting votes for Option B).\n"
        "Example: <code>40</code>"
    )


@router.message(PollState.base_b)
async def poll_base_b(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    n = _parse_int(raw)
    if n is None or n < 0:
        await message.answer("base_b must be a non-negative integer. Try again.")
        return

    data = await state.get_data()
    asset_name = data.get("asset_name")
    question = str(data.get("question") or "").strip()
    option_a = str(data.get("option_a") or "").strip()
    option_b = str(data.get("option_b") or "").strip()
    base_a = int(data.get("base_a") or 0)
    base_b = int(n)

    if not question or not option_a or not option_b:
        await message.answer("Missing poll data. Please run /poll_create again.")
        await state.clear()
        return

    # Step 7: ask end time (minutes from now) before we create the poll.
    await state.update_data(base_b=base_b, end_after_minutes=n)
    await state.set_state(PollState.end_after_minutes)
    await message.answer(
        "Step 7/7: Send <b>end_after_minutes</b> (integer, vote is closed after this time).\n"
        "Example: <code>60</code> means 60 minutes from now (UTC).\n"
        "Send <code>0</code> to close immediately."
    )


@router.message(PollState.end_after_minutes)
async def poll_end_after_minutes(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    minutes = _parse_int(raw)
    if minutes is None or minutes < 0:
        await message.answer("end_after_minutes must be a non-negative integer. Try again.")
        return

    data = await state.get_data()
    asset_name = data.get("asset_name")
    question = str(data.get("question") or "").strip()
    option_a = str(data.get("option_a") or "").strip()
    option_b = str(data.get("option_b") or "").strip()
    base_a = int(data.get("base_a") or 0)
    base_b = int(data.get("base_b") or 0)

    if not question or not option_a or not option_b:
        await message.answer("Missing poll data. Please run /poll_create again.")
        await state.clear()
        return

    poll_id = uuid4().hex[:8]
    settings = load_settings()
    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()

    created_at = datetime.now(tz=timezone.utc)
    end_at = created_at + timedelta(minutes=minutes)

    await db.save_smart_poll(
        poll_id=poll_id,
        asset_name=str(asset_name) if asset_name else None,
        question=question,
        option_a=option_a,
        option_b=option_b,
        base_a=base_a,
        base_b=base_b,
        end_at=end_at,
        created_at=created_at,
    )
    await db.close()
    await state.clear()

    asset_line = f"Asset: <code>{asset_name}</code>\n" if asset_name else ""
    await message.answer(
        "<b>Smart poll saved</b>\n\n"
        f"ID: <code>{poll_id}</code>\n"
        f"{asset_line}"
        f"Question: {question}\n"
        f"A: {option_a} (base={base_a})\n"
        f"B: {option_b} (base={base_b})\n"
        f"Voting ends at: <code>{end_at.isoformat(timespec='seconds')}</code>\n\n"
        "You can now wire this poll_id into future flows or broadcasts."
    )

    # Deep link activation button: https://t.me/<VoteBotUsername>?start=vote_<poll_id>
    vote_username = (settings.vote_bot_username or "").strip()
    if not vote_username:
        me = await message.bot.me()
        vote_username = (me.username or "").strip() if me else ""
    if vote_username:
        vote_url = f"https://t.me/{vote_username}?start=vote_{poll_id}"
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Vote now", url=vote_url)],
            ]
        )
        await message.answer(
            "<b>Poll activation</b>\n"
            "Send this button to users:\n"
            f"{vote_url}",
            reply_markup=kb,
            disable_web_page_preview=True,
        )


@router.message(Command("poll_publish", ignore_mention=True))
async def poll_publish(message: Message) -> None:
    """
    Publish a smart poll button to a target chat (channel/group).
    Usage: /poll_publish <poll_id> <target_chat>
    """
    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            "Usage: <code>/poll_publish &lt;poll_id&gt; &lt;target_chat&gt;</code>\n"
            "Example: <code>/poll_publish f080cad9 -1001234567890</code>"
        )
        return

    poll_id = parts[1].strip()
    target_chat = parts[2].strip()

    settings = load_settings()
    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()
    poll = await db.get_smart_poll(poll_id=poll_id)
    await db.close()

    if not poll:
        await message.answer("Poll not found. Create it first with <code>/poll_create</code>.")
        return

    vote_username = (settings.vote_bot_username or "").strip()
    if not vote_username:
        # Fallback: try to use this bot's own username (but normally you should set VOTE_BOT_USERNAME).
        me = await message.bot.me()
        vote_username = (me.username or "").strip() if me else ""

    if not vote_username:
        await message.answer("Missing vote bot username. Set <code>VOTE_BOT_USERNAME</code> in env.")
        return

    vote_url = f"https://t.me/{vote_username}?start=vote_{poll_id}"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Vote now", url=vote_url)],
        ]
    )

    question = poll["question"]
    base_a = poll["base_a"]
    base_b = poll["base_b"]
    end_at = poll.get("end_at")

    text = (
        f"📊 {question}\n\n"
        f"A: {poll['option_a']} (base={base_a})\n"
        f"B: {poll['option_b']} (base={base_b})"
        + (f"\n\n⏱️ Voting ends at: {end_at}" if end_at else "")
    )

    # If the poll has an asset name, try to send as photo/video. Otherwise fallback to text.
    if poll.get("asset_name"):
        db2 = SqliteDatabase(settings.db_url)
        await db2.connect()
        await db2.init_schema()
        asset = await db2.get_asset(name=poll["asset_name"])
        await db2.close()
        if asset:
            try:
                if asset.get("file_type") == "photo":
                    await message.bot.send_photo(
                        chat_id=target_chat,
                        photo=asset["file_id"],
                        caption=text,
                        reply_markup=kb,
                    )
                    await message.answer("Poll published successfully ✅")
                    return
                if asset.get("file_type") == "video":
                    await message.bot.send_video(
                        chat_id=target_chat,
                        video=asset["file_id"],
                        caption=text,
                        reply_markup=kb,
                    )
                    await message.answer("Poll published successfully ✅")
                    return
            except Exception:
                # Fallback to text message.
                pass

    try:
        await message.bot.send_message(
            chat_id=target_chat,
            text=text,
            reply_markup=kb,
            disable_web_page_preview=True,
        )
    except Exception:
        await message.answer("Publish failed. Check bot permission in the target chat.")
        return

    await message.answer("Poll published successfully ✅")

