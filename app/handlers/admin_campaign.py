from __future__ import annotations

from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.config import load_settings
from app.db.sqlite import SqliteDatabase
from app.filters import IsAdmin
from app.localization.locales import term

router = Router(name="admin_campaign")
router.message.filter(IsAdmin())


class CampaignState(StatesGroup):
    target_chat = State()
    asset_name = State()
    caption = State()
    buttons = State()
    confirm = State()


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


async def _send_campaign_preview(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    rows: list[list[dict]] = [row for row in data.get("button_rows", []) if row]
    kb = _build_inline_keyboard(rows)
    caption = data.get("caption", "")
    asset = data.get("asset")

    await state.update_data(button_rows=rows)
    await state.set_state(CampaignState.confirm)
    await message.answer(
        "<b>Step 5/5: Preview ready</b>\n\n"
        "If this looks good, send <code>/publish</code>.\n"
        "If you need to restart, send <code>/campaign_cancel</code>."
    )
    if asset and asset.get("file_type") == "photo":
        await message.answer_photo(photo=asset["file_id"], caption=caption, reply_markup=kb)
    elif asset and asset.get("file_type") == "video":
        await message.answer_video(video=asset["file_id"], caption=caption, reply_markup=kb)
    else:
        await message.answer(caption, reply_markup=kb, disable_web_page_preview=True)


@router.message(Command("operator_help", ignore_mention=True))
async def operator_help(message: Message) -> None:
    await message.answer(
        "<b>Operator Commands (English)</b>\n\n"
        "• <code>/campaign_create</code> - Create a channel promotion post (guided)\n"
        "• <code>/asset_save NAME</code> - Save replied photo/video as reusable file_id\n"
        "• <code>/template_save NAME</code> - Save current button layout as template\n"
        "• <code>/template_apply NAME</code> - Apply template in Step 3/4 (after asset)\n"
        "• <code>/template_delete NAME</code> - Delete a saved template\n"
        "• <code>/template_list</code> - List available templates\n"
        "• <code>/campaign_cancel</code> - Cancel active builder flow\n\n"
        "Tip: Use <code>/campaign_create</code> for fast channel campaign posting."
    )


@router.message(Command("ops_flow", ignore_mention=True))
async def ops_flow(message: Message) -> None:
    await message.answer(
        "<b>Operator Ops Flow (Fast)</b>\n\n"
        "1) Save reusable media:\n"
        "   Reply to photo/video -> <code>/asset_save promo1</code>\n"
        "2) Build campaign:\n"
        "   <code>/campaign_create</code>\n"
        "3) Option A: Enter English draft + buttons\n"
        "4) Option B (faster): <code>/template_apply name</code> after Step 2\n"
        "5) Save reusable template: <code>/template_save name</code>\n"
        "6) <code>/done</code> -> preview -> <code>/publish</code>\n\n"
        "<b>CTA Suggestions</b>\n"
        f"EN: {term('core', 'JOIN_NOW', 'en')} | {term('sports', 'BEST_ODDS', 'en')}\n"
        f"PH: {term('core', 'JOIN_NOW', 'ph')} | {term('sports', 'BEST_ODDS', 'ph')}\n"
        f"VI: {term('core', 'JOIN_NOW', 'vi')} | {term('sports', 'BEST_ODDS', 'vi')}\n"
        f"TR: {term('core', 'JOIN_NOW', 'tr')} | {term('sports', 'BEST_ODDS', 'tr')}\n"
        f"ES: {term('core', 'JOIN_NOW', 'es')} | {term('sports', 'BEST_ODDS', 'es')}\n"
    )


def _guess_asset_from_reply(message: Message) -> tuple[str, str] | None:
    if not message.reply_to_message:
        return None
    m = message.reply_to_message
    if m.photo:
        return ("photo", m.photo[-1].file_id)
    if m.video:
        return ("video", m.video.file_id)
    return None


@router.message(Command("asset_save", ignore_mention=True))
async def asset_save(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Reply to a photo/video then send: <code>/asset_save name</code>")
        return
    name = parts[1].strip()
    got = _guess_asset_from_reply(message)
    if not got:
        await message.answer("Please reply to a photo or video message first.")
        return
    file_type, file_id = got

    settings = load_settings()
    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()
    await db.save_asset(name=name, file_id=file_id, file_type=file_type, created_at=datetime.now(tz=timezone.utc))
    await db.close()
    await message.answer(f"Asset saved: <b>{name}</b> ({file_type})")


@router.message(Command("campaign_create", ignore_mention=True))
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


@router.message(Command("campaign_cancel", ignore_mention=True))
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


@router.message(CampaignState.caption, F.text & ~F.text.startswith("/"))
async def campaign_caption(message: Message, state: FSMContext) -> None:
    caption = (message.text or "").strip()
    await state.update_data(caption=caption, button_rows=[[]])
    await state.set_state(CampaignState.buttons)
    await message.answer(
        "Step 4/5: Add CTA buttons using this format:\n"
        "<code>Button Text | https://your-link.com</code>\n\n"
        "Commands:\n"
        "• <code>/row</code> -> start a new row\n"
        "• <code>/done</code> -> finish and preview\n"
        "• <code>/campaign_cancel</code> -> cancel"
    )


@router.message(CampaignState.buttons, Command("row", ignore_mention=True))
async def campaign_row(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    rows: list[list[dict]] = data.get("button_rows", [[]])
    rows.append([])
    await state.update_data(button_rows=rows)
    await message.answer("Started a new button row.")


@router.message(CampaignState.buttons, Command("done", ignore_mention=True))
async def campaign_done(message: Message, state: FSMContext) -> None:
    await _send_campaign_preview(message, state)


@router.message(CampaignState.buttons, F.text & ~F.text.startswith("/"))
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


@router.message(Command("template_list", ignore_mention=True))
async def template_list(message: Message) -> None:
    settings = load_settings()
    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()
    items = await db.list_campaign_templates(limit=50)
    await db.close()
    if not items:
        await message.answer("No templates yet. Build one and save with <code>/template_save NAME</code>.")
        return
    lines = ["<b>Campaign Templates</b>"]
    for item in items:
        lines.append(f"• <code>{item['name']}</code>")
    lines.append("\nUse in campaign Step 3/4: <code>/template_apply NAME</code>")
    await message.answer("\n".join(lines))


@router.message(Command("template_save", ignore_mention=True))
async def template_save(message: Message, state: FSMContext) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: <code>/template_save NAME</code>")
        return
    name = parts[1].strip().lower()
    data = await state.get_data()
    rows: list[list[dict]] = [row for row in data.get("button_rows", []) if row]
    if not rows:
        await message.answer("No button layout found. Add buttons first, then save template.")
        return
    settings = load_settings()
    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()
    await db.save_campaign_template(
        name=name,
        button_rows=rows,
        created_at=datetime.now(tz=timezone.utc),
    )
    await db.close()
    await message.answer(f"Template saved: <b>{name}</b> ({sum(len(r) for r in rows)} buttons)")


@router.message(Command("template_delete", ignore_mention=True))
async def template_delete(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: <code>/template_delete NAME</code>")
        return
    name = parts[1].strip().lower()
    settings = load_settings()
    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()
    ok = await db.delete_campaign_template(name=name)
    await db.close()
    if not ok:
        await message.answer("Template not found.")
        return
    await message.answer(f"Template deleted: <b>{name}</b>")


@router.message(CampaignState.caption, Command("template_apply", ignore_mention=True))
@router.message(CampaignState.buttons, Command("template_apply", ignore_mention=True))
async def template_apply(message: Message, state: FSMContext) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: <code>/template_apply NAME</code>")
        return
    name = parts[1].strip().lower()
    settings = load_settings()
    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()
    tpl = await db.get_campaign_template(name=name)
    await db.close()
    if not tpl:
        await message.answer("Template not found. Check <code>/template_list</code>.")
        return
    rows = [row for row in tpl.get("button_rows", []) if row]
    await state.update_data(button_rows=rows)
    await state.set_state(CampaignState.buttons)
    await message.answer(
        f"Template applied: <b>{name}</b> ({sum(len(r) for r in rows)} buttons)\n"
        "You can add/edit buttons now, then send <code>/done</code>."
    )


@router.message(CampaignState.confirm, Command("publish", ignore_mention=True))
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

