import logging
from fastapi import FastAPI
from app.config import settings
from sqlalchemy import text
from app.db import engine
from app.routes.trips import router as trips_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title = settings.app_name,
    version = settings.api_version
)

app.include_router(trips_router)


@app.on_event("startup")
def startup_event():
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "environment": settings.environment
    }


@app.get("/ready")
def ready():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception as e:
        logger.exception("DB readiness check failed")
        return {"ready": False, "error": str(e)}