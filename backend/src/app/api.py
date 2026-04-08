from fastapi import APIRouter

from modules.sessions.router import router as sessions_router
from modules.stages.router import router as stages_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(sessions_router)
api_router.include_router(stages_router)
