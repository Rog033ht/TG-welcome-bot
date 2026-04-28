import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import Settings, load_settings
from app.db.sqlite import SqliteDatabase
from app.handlers import router as root_router
from app.middlewares.user_tracking import UserTrackingMiddleware
from app.services.broadcasts import BroadcastService
from app.services.followups import FollowupService
from app.utils.logging import setup_logging


async def _run() -> None:
    settings: Settings = load_settings()
    setup_logging(settings.log_level)

    db = SqliteDatabase(settings.db_url)
    await db.connect()
    await db.init_schema()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    followups = FollowupService(db=db, settings=settings)
    bot["followups"] = followups
    broadcasts = BroadcastService(db=db, settings=settings)
    bot["broadcasts"] = broadcasts

    dp = Dispatcher(storage=MemoryStorage())

    dp.update.middleware(UserTrackingMiddleware(db=db))
    dp.include_router(root_router)

    scheduler_task = asyncio.create_task(followups.run(bot))
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await followups.stop()
        scheduler_task.cancel()
        await db.close()


def main() -> None:
    asyncio.run(_run())

