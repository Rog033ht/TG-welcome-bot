from aiogram import Router

from app.handlers.admin_broadcast import router as admin_broadcast_router
from app.handlers.admin_campaign import router as admin_campaign_router
from app.handlers.admin_poll import router as admin_poll_router

router = Router(name="admin_root")
router.include_router(admin_campaign_router)
router.include_router(admin_broadcast_router)
router.include_router(admin_poll_router)

__all__ = ["router"]

