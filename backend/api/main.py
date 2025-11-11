from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from logging import INFO, basicConfig

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from pydantic import BaseModel
from api.config import config
from api.views.auth import router as auth_router
from api.views.compute import router as compute_router
from api.views.files import router as files_router
from api.views.properties import router as properties_router

basicConfig(level=INFO)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield


app = FastAPI(root_path=config.PATH_PREFIX, lifespan=lifespan)

origins = [config.APP_URL] if config.APP_URL else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


@app.get(
    "/healthz",
    tags=["Healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
async def get_health() -> HealthCheck:
    """Endpoint to perform an API healthcheck."""

    return HealthCheck(status="OK")


app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

app.include_router(
    compute_router,
    prefix="/compute",
    tags=["Compute"],
)

app.include_router(
    files_router,
    prefix="/files",
    tags=["Files"],
)

app.include_router(
    properties_router,
    prefix="/properties",
    tags=["Properties"],
)
