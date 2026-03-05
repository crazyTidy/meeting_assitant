"""Application entry point."""
import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.router import api_router
from app.middleware.dev_auth import dev_auth_middleware
from app.middleware.auth import auth_middleware


def setup_logging():
    """Configure application logging."""
    # Get log level from settings
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Create format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # Set specific loggers to the desired level
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("fastapi").setLevel(log_level)
    logging.getLogger("app").setLevel(log_level)

    logging.info(f"Logging configured at {logging.getLevelName(log_level)} level")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Setup logging first
    setup_logging()

    # Startup
    await init_db()

    # Ensure upload directory exists
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    yield

    # Shutdown
    pass


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Development mode authentication (for testing)
if settings.DEV_MODE:
    app.middleware("http")(dev_auth_middleware)
else:
    # Production JWT authentication
    app.middleware("http")(auth_middleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}
