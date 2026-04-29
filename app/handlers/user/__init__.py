from aiogram import Router

from app.handlers.callbacks import router as callbacks_router
from app.handlers.content import router as content_router
from app.handlers.spin import router as spin_router
from app.handlers.start import router as start_router

router = Router(name="user_root")
router.include_router(start_router)
router.include_router(content_router)
router.include_router(spin_router)
router.include_router(callbacks_router)

__all__ = ["router"]

