from fastapi import FastAPI

from app.core.config import Settings, settings
from app.core.logging import setup_logging
from app.routers.health import router as health_router


def create_app(config: Settings = settings) -> FastAPI:
    setup_logging(debug=config.ENV == "dev")
    app = FastAPI(title=config.APP_NAME, debug=config.ENV == "dev")
    app.include_router(health_router, prefix="/health", tags=["health"])
    return app


app = create_app()
