from collections.abc import AsyncGenerator, Callable
from contextlib import _AsyncGeneratorContextManager, asynccontextmanager
from typing import Any

import anyio
import fastapi
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi


from ..models import *  # noqa: F403
from .config import (
    EnvironmentOption,
    Settings,
    settings,
)
from .db.database import Base
from .db.database import async_engine as engine


# -------------- database --------------
async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# -------------- application --------------
async def set_threadpool_tokens(number_of_tokens: int = 100) -> None:
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = number_of_tokens


def lifespan_factory(
    settings: Settings,
    create_tables_on_start: bool = True,
) -> Callable[[FastAPI], _AsyncGeneratorContextManager[Any]]:
    """Factory to create a lifespan async context manager for a FastAPI app."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        from asyncio import Event

        initialization_complete = Event()
        app.state.initialization_complete = initialization_complete

        await set_threadpool_tokens()

        try:
            # Phase 1: Disable Redis/ARQ initialization
            # if isinstance(settings, RedisCacheSettings):
            #     await create_redis_cache_pool()

            # if isinstance(settings, RedisQueueSettings):
            #     await create_redis_queue_pool()

            # if isinstance(settings, RedisRateLimiterSettings):
            #     await create_redis_rate_limit_pool()

            # Phase 1: Disable table creation to avoid external database requirement
            # if create_tables_on_start:
            #     await create_tables()

            initialization_complete.set()

            yield

        finally:
            # Phase 1: Disable Redis/ARQ cleanup
            # if isinstance(settings, RedisCacheSettings):
            #     await close_redis_cache_pool()

            # if isinstance(settings, RedisQueueSettings):
            #     await close_redis_queue_pool()

            # if isinstance(settings, RedisRateLimiterSettings):
            #     await close_redis_rate_limit_pool()
            pass

    return lifespan


# -------------- application --------------
def create_application(
    router: APIRouter,
    settings: Settings,
    create_tables_on_start: bool = True,
    lifespan: Callable[[FastAPI], _AsyncGeneratorContextManager[Any]] | None = None,
    **kwargs: Any,
) -> FastAPI:
    """Creates and configures a FastAPI application based on the provided settings.

    This function initializes a FastAPI application and configures it with the
    provided Settings object containing app metadata, database, CORS, and environment configuration.

    Parameters
    ----------
    router : APIRouter
        The APIRouter object containing the routes to be included in the FastAPI application.

    settings
        An instance representing the settings for configuring the FastAPI application.
        It determines the configuration applied:

        - AppSettings: Configures basic app metadata like name, description, contact, and license info.
        The Settings object containing all application configuration including:
        - App metadata (name, description, contact, license info)
        - Database configuration (PostgreSQL connection settings)
        - CORS configuration (origins, methods, headers)
        - Environment settings (local, staging, production)

    create_tables_on_start : bool
        A flag to indicate whether to create database tables on application startup.
        Defaults to True.

    **kwargs
        Additional keyword arguments passed directly to the FastAPI constructor.

    Returns
    -------
    FastAPI
        A fully configured FastAPI application instance.

    The function configures the FastAPI application with different features and behaviors
    based on the provided settings. It includes setting up database connections and customizing 
    the API documentation based on the environment settings.
    """
    # --- before creating application ---
    to_update = {
        "title": settings.APP_NAME,
        "description": settings.APP_DESCRIPTION,
        "contact": {"name": settings.CONTACT_NAME, "email": settings.CONTACT_EMAIL},
        "license_info": {"name": settings.LICENSE_NAME},
        "version": settings.APP_VERSION,
    }
    kwargs.update(to_update)

    # Disable docs in production
    kwargs.update({"docs_url": None, "redoc_url": None, "openapi_url": None})

    # Use custom lifespan if provided, otherwise use default factory
    if lifespan is None:
        lifespan = lifespan_factory(settings, create_tables_on_start=create_tables_on_start)

    application = FastAPI(lifespan=lifespan, **kwargs)
    application.include_router(router)



    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )

    # Environment-specific documentation setup
    if settings.ENVIRONMENT != EnvironmentOption.PRODUCTION:
        docs_router = APIRouter()
        if settings.ENVIRONMENT != EnvironmentOption.LOCAL:
            docs_router = APIRouter()

        @docs_router.get("/docs", include_in_schema=False)
        async def get_swagger_documentation() -> fastapi.responses.HTMLResponse:
            return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

        @docs_router.get("/redoc", include_in_schema=False)
        async def get_redoc_documentation() -> fastapi.responses.HTMLResponse:
            return get_redoc_html(openapi_url="/openapi.json", title="docs")

        @docs_router.get("/openapi.json", include_in_schema=False)
        async def openapi() -> dict[str, Any]:
            out: dict = get_openapi(title=application.title, version=application.version, routes=application.routes)
            return out

        application.include_router(docs_router)

    return application
