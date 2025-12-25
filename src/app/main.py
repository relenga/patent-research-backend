from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .api import router
from .core.config import settings
from .core.setup import create_application, lifespan_factory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager."""
    # Get the default lifespan
    default_lifespan = lifespan_factory(settings)

    # Run the default lifespan
    async with default_lifespan(app):
        yield


app = create_application(router=router, settings=settings, lifespan=lifespan)

# Add root endpoint to redirect to documentation
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root URL to API documentation."""
    return RedirectResponse(url="/docs")
