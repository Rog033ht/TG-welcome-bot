from aiogram import Router

from app.handlers.admin import router as admin_router
from app.handlers.user import router as user_router

router = Router(name="root")
router.include_router(user_router)
router.include_router(admin_router)

__all__ = ["router"]

