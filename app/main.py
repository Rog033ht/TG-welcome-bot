import asyncio

from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import Settings, load_settings
from app.db.sqlite import SqliteDatabase
from app.handlers import router as root_router
from app.middlewares.language import LanguageMiddleware
from app.middlewares.user_tracking import UserTrackingMiddleware
from app.services.broadcasts import BroadcastService
from app.utils.logging import setup_logging
from app.utils.process_lock import ProcessLock


async def _run() -> None:
    settings: Settings = load_settings()
    setup_logging(settings.log_level)
    if (settings.gemini_api_key or "").strip():
        logger.info(
            "Gemini: GEMINI_API_KEY is set (model={}); campaign AI translations enabled.",
            settings.gemini_model,
        )
    else:
        logger.warning(
            "Gemini: GEMINI_API_KEY missing or blank — /campaign_create PH/VI/TR/ES will mirror English.",
        )
    lock = ProcessLock(key=settings.bot_token)
    if not lock.acquire():
        raise RuntimeError("Another bot instance is already running for this token.")

    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    # If this bot token was previously used elsewhere (webhook mode),
    # long-polling won't receive updates until webhook is removed.
    await bot.delete_webhook(drop_pending_updates=True)

    dp = Dispatcher(storage=MemoryStorage())
    # Store shared DB in Dispatcher context (aiogram DI friendly)
    dp["db"] = db
    dp["broadcasts"] = BroadcastService(db=db, settings=settings)

    dp.update.middleware(LanguageMiddleware())
    dp.update.middleware(UserTrackingMiddleware(db=db))
    dp.include_router(root_router)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await db.close()
        lock.release()


def main() -> None:
    asyncio.run(_run())

