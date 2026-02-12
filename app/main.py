import logging
from fastapi import FastAPI
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title = settings.app_name,
    version = settings.api_version
)


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
    return {"ready": True}
