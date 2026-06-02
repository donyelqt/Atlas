from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes.analyze import router as api_router
from app.api.routes.neo4j import router as neo4j_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield


def create_app() -> FastAPI:
    _app = FastAPI(
        title="Atlas API",
        description="AI-powered repository intelligence platform",
        version="0.1.0",
        lifespan=lifespan,
    )
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _app.include_router(api_router, prefix="/api")
    _app.include_router(neo4j_router, prefix="/api")

    @_app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    return _app
