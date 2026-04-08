from fastapi import FastAPI

from app.api import api_router
from app.deps import make_response
from core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(api_router)


@app.get("/health")
def healthcheck() -> dict[str, object]:
    return make_response({"status": "ok", "environment": settings.app_env})
