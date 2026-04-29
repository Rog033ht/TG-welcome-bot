from __future__ import annotations

from dataclasses import dataclass

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.config import load_settings
from app.db.sqlite import SqliteDatabase
from app.filters import IsAdmin

router = Router(name="admin_campaign")
router.message.filter(IsAdmin())


class CampaignState(StatesGroup):
    target_chat = State()
    asset_name = State()
    caption = State()
    buttons = State()
    confirm = State()


@dataclass
class ButtonItem:
    text: str
    url: str


def _build_inline_keyboard(rows: list[list[dict]]) -> InlineKeyboardMarkup | None:
    if not rows:
        return None
    output_rows: list[list[InlineKeyboardButton]] = []
    for row in rows:
        if not row:
            continue
        output_rows.append([InlineKeyboardButton(text=item["text"], url=item["url"]) for item in row])
    if not output_rows:
        return None
    return InlineKeyboardMarkup(inline_keyboard=output_rows)


@router.message(Command("operator_help"))
async def operator_help(message: Message) -> None:
    await message.answer(
        "<b>Operator Commands (English)</b>\n\n"
        "• <code>/campaign_create</code> - Create a channel promotion post (guided)\n"
        "• <code>/asset_save NAME</code> - Save replied photo/video as reusable file_id\n"
        "• <code>/broadcast_new asset | caption</code> - Create mass broadcast job\n"
        "• <code>/broadcast_run ID</code> - Run a broadcast\n"
        "• <code>/broadcast_pause ID</code> - Pause a broadcast\n"
        "• <code>/broadcast_status ID</code> - Check broadcast progress\n\n"
        "Tip: Use <code>/campaign_create</code> for fast channel campaign posting."
    )


@router.message(Command("campaign_create"))
async def campaign_create(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(CampaignState.target_chat)
    await message.answer(
        "<b>Campaign Builder</b>\n\n"
        "Step 1/5: Send target channel/chat.\n"
        "Examples:\n"
        "• <code>@your_channel</code>\n"
        "• <code>-1001234567890</code>\n\n"
        "You can cancel anytime with <code>/campaign_cancel</code>."
    )


@router.message(Command("campaign_cancel"))
async def campaign_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Campaign builder canceled.")


@router.message(CampaignState.target_chat, F.text)
async def campaign_target_chat(message: Message, state: FSMContext) -> None:
    target = (message.text or "").strip()
    await state.update_data(target_chat=target)
    await state.set_state(CampaignState.asset_name)
    await message.answer(
        "Step 2/5: Send asset name (saved via <code>/asset_save</code>) or type <code>skip</code>."
    )


@router.message(CampaignState.asset_name, F.text)
async def campaign_asset(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if raw.lower() == "skip":
        await state.update_data(asset_name=None, asset=None)
        await state.set_state(CampaignState.caption)
        await message.answer("Step 3/5: Send campaign caption text (HTML allowed).")
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

    await state.update_data(asset_name=raw, asset=asset)
    await state.set_state(CampaignState.caption)
    await message.answer("Step 3/5: Send campaign caption text (HTML allowed).")


@router.message(CampaignState.caption, F.text)
async def campaign_caption(message: Message, state: FSMContext) -> None:
    caption = (message.text or "").strip()
    await state.update_data(caption=caption, button_rows=[[]])
    await state.set_state(CampaignState.buttons)
    await message.answer(
        "Step 4/5: Add buttons using this format:\n"
        "<code>Button Text | https://your-link.com</code>\n\n"
        "Commands:\n"
        "• <code>/row</code> -> start a new row\n"
        "• <code>/done</code> -> finish and preview\n"
        "• <code>/campaign_cancel</code> -> cancel"
    )


@router.message(CampaignState.buttons, Command("row"))
async def campaign_row(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    rows: list[list[dict]] = data.get("button_rows", [[]])
    rows.append([])
    await state.update_data(button_rows=rows)
    await message.answer("Started a new button row.")


@router.message(CampaignState.buttons, Command("done"))
async def campaign_done(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    rows: list[list[dict]] = data.get("button_rows", [[]])
    rows = [row for row in rows if row]
    kb = _build_inline_keyboard(rows)

    await state.update_data(button_rows=rows)
    await state.set_state(CampaignState.confirm)

    preview_text = (
        "<b>Step 5/5: Preview ready</b>\n\n"
        "If this looks good, send <code>/publish</code>.\n"
        "If you need to restart, send <code>/campaign_cancel</code>."
    )
    await message.answer(preview_text)

    data = await state.get_data()
    caption = data.get("caption", "")
    asset = data.get("asset")
    if asset and asset.get("file_type") == "photo":
        await message.answer_photo(photo=asset["file_id"], caption=caption, reply_markup=kb)
    elif asset and asset.get("file_type") == "video":
        await message.answer_video(video=asset["file_id"], caption=caption, reply_markup=kb)
    else:
        await message.answer(caption, reply_markup=kb, disable_web_page_preview=True)


@router.message(CampaignState.buttons, F.text)
async def campaign_add_button(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if "|" not in raw:
        await message.answer("Invalid format. Use: <code>Button Text | https://your-link.com</code>")
        return
    text, url = [p.strip() for p in raw.split("|", 1)]
    if not text or not url.startswith("http"):
        await message.answer("Invalid button. URL must start with http/https.")
        return

    data = await state.get_data()
    rows: list[list[dict]] = data.get("button_rows", [[]])
    if not rows:
        rows = [[]]
    rows[-1].append({"text": text, "url": url})
    await state.update_data(button_rows=rows)
    await message.answer(f"Added button: <b>{text}</b>")


@router.message(CampaignState.confirm, Command("publish"))
async def campaign_publish(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    target_chat = data.get("target_chat")
    caption = data.get("caption", "")
    asset = data.get("asset")
    rows: list[list[dict]] = data.get("button_rows", [])
    kb = _build_inline_keyboard(rows)

    if not target_chat:
        await message.answer("Missing target chat. Run <code>/campaign_create</code> again.")
        await state.clear()
        return

    try:
        if asset and asset.get("file_type") == "photo":
            await message.bot.send_photo(chat_id=target_chat, photo=asset["file_id"], caption=caption, reply_markup=kb)
        elif asset and asset.get("file_type") == "video":
            await message.bot.send_video(chat_id=target_chat, video=asset["file_id"], caption=caption, reply_markup=kb)
        else:
            await message.bot.send_message(chat_id=target_chat, text=caption, reply_markup=kb, disable_web_page_preview=True)
    except Exception as e:
        await message.answer(f"Publish failed: <code>{type(e).__name__}</code>\nCheck bot permission in target channel.")
        return

    await message.answer("Campaign published successfully.")
    await state.clear()

