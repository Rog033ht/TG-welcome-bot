from __future__ import annotations

from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import load_settings
from app.db.sqlite import SqliteDatabase
from app.filters import IsAdmin
from app.services.broadcasts import BroadcastService

router = Router(name="admin_broadcast")
router.message.filter(IsAdmin())


def _guess_asset_from_reply(message: Message) -> tuple[str, str] | None:
    """
    Returns (file_type, file_id) from replied message.
    Supports: photo, video.
    """
    if not message.reply_to_message:
        return None
    m = message.reply_to_message
    if m.photo:
        return ("photo", m.photo[-1].file_id)
    if m.video:
        return ("video", m.video.file_id)
    return None


@router.message(Command("asset_save"))
async def asset_save(message: Message) -> None:
    """
    Usage:
      Reply to a photo/video then: /asset_save name_here
    """
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Reply sa photo/video then: <code>/asset_save name</code>")
        return
    name = parts[1].strip()
    got = _guess_asset_from_reply(message)
    if not got:
        await message.answer("Boss, reply ka muna sa photo or video message.")
        return
    file_type, file_id = got

    settings = load_settings()
    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()
    await db.save_asset(name=name, file_id=file_id, file_type=file_type, created_at=datetime.now(tz=timezone.utc))
    await db.close()

    await message.answer(f"✅ Saved asset: <b>{name}</b>\nType: <code>{file_type}</code>")


@router.message(Command("broadcast_new"))
async def broadcast_new(message: Message) -> None:
    """
    Usage:
      /broadcast_new asset_name | caption text...
    """
    raw = (message.text or "").replace("/broadcast_new", "", 1).strip()
    if "|" not in raw:
        await message.answer("Usage: <code>/broadcast_new asset_name | caption...</code>")
        return
    asset_name, caption = [p.strip() for p in raw.split("|", 1)]
    if not asset_name or not caption:
        await message.answer("Usage: <code>/broadcast_new asset_name | caption...</code>")
        return

    settings = load_settings()
    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()
    asset = await db.get_asset(name=asset_name)
    if not asset:
        await message.answer("Asset not found. Save first via <code>/asset_save</code>.")
        await db.close()
        return

    broadcast_id = await db.create_broadcast(asset_name=asset_name, caption=caption, created_at=datetime.now(tz=timezone.utc))
    await db.close()

    await message.answer(f"🚀 Broadcast created: <code>{broadcast_id}</code>\nUse: <code>/broadcast_run {broadcast_id}</code>")


@router.message(Command("broadcast_run"))
async def broadcast_run(message: Message, broadcasts: BroadcastService) -> None:
    """
    Usage:
      /broadcast_run 123
    """
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: <code>/broadcast_run BROADCAST_ID</code>")
        return
    try:
        broadcast_id = int(parts[1].strip())
    except ValueError:
        await message.answer("Invalid broadcast id.")
        return

    await broadcasts.start_or_resume(bot=message.bot, broadcast_id=broadcast_id)
    await message.answer(f"▶️ Running broadcast <code>{broadcast_id}</code> (throttle: {load_settings().broadcast_rps}/sec)")


@router.message(Command("broadcast_pause"))
async def broadcast_pause(message: Message, broadcasts: BroadcastService) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: <code>/broadcast_pause BROADCAST_ID</code>")
        return
    try:
        broadcast_id = int(parts[1].strip())
    except ValueError:
        await message.answer("Invalid broadcast id.")
        return

    await broadcasts.pause(broadcast_id)
    await message.answer(f"⏸ Paused broadcast <code>{broadcast_id}</code> (pwede i-resume via /broadcast_run).")


@router.message(Command("broadcast_status"))
async def broadcast_status(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: <code>/broadcast_status BROADCAST_ID</code>")
        return
    try:
        broadcast_id = int(parts[1].strip())
    except ValueError:
        await message.answer("Invalid broadcast id.")
        return

    settings = load_settings()
    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()
    job = await db.get_broadcast(broadcast_id=broadcast_id)
    await db.close()

    if not job:
        await message.answer("Broadcast not found.")
        return
    await message.answer(
        "📊 <b>Broadcast Status</b>\n"
        f"ID: <code>{job['id']}</code>\n"
        f"Asset: <code>{job['asset_name']}</code>\n"
        f"Status: <b>{job['status']}</b>\n"
        f"Last UID: <code>{job['last_uid']}</code>\n"
        f"Sent: <b>{job['sent_count']}</b>\n"
        f"Failed: <b>{job['fail_count']}</b>\n"
    )

