"""Application entry point.

Follows the Single Responsibility Principle by only handling application setup.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
<<<<<<< HEAD
from app.core.logging import configure_logging, get_logger
from app.core.logging.middleware import (
    CorrelationIdMiddleware,
    RequestLoggingMiddleware,
)

logger = get_logger(__name__)
=======
from app.core.logging import setup_logging
from app.db.database import db

>>>>>>> origin/main


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
<<<<<<< HEAD
    configure_logging(
        level=settings.LOG_LEVEL,
        format_type=settings.LOG_FORMAT,
        propagate=False,
    )
    logger.info(
        f"Starting {settings.APP_NAME} v{settings.APP_VERSION}",
        extra={
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        },
    )
    yield
    # Shutdown
    logger.info("Application shutting down")
=======
    setup_logging()
    await db.connect()       # ← conectar MongoDB al arrancar
    yield
    # Shutdown
    await db.disconnect()    # ← desconectar al cerrar
>>>>>>> origin/main


def create_application() -> FastAPI:
    """
    Application factory pattern.

    Creates and configures the FastAPI application instance.
    Follows Factory Pattern for better testability.
    """
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Logging middleware (before CORS to capture all requests)
    if settings.LOG_CORRELATION_ID:
        application.add_middleware(CorrelationIdMiddleware)
    if settings.DEBUG:
        application.add_middleware(RequestLoggingMiddleware)

    # CORS Middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    application.include_router(api_router, prefix="/api/v1")

    return application


app = create_application()


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {"status": "healthy", "version": settings.APP_VERSION}
