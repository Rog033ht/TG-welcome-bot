from aiogram import Router

from app.handlers.admin_campaign import router as admin_campaign_router
from app.handlers.callbacks import router as callbacks_router
from app.handlers.content import router as content_router
from app.handlers.spin import router as spin_router
from app.handlers.start import router as start_router

router = Router(name="root")
router.include_router(start_router)
router.include_router(content_router)
router.include_router(spin_router)
router.include_router(callbacks_router)
router.include_router(admin_campaign_router)

__all__ = ["router"]

