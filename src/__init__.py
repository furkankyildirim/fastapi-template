from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from src.utils.http import client
from src.errors.generic import ValidationError, HTTPError

from src.configs import AppConfig
from . import routers
from src.middlewares import GlobalExceptionHandlerMiddleware, RequestLoggerMiddleware, SessionMiddleware
from .utils.common import format_validation_error

@asynccontextmanager
async def app_lifespan(app):
    await client.start()
    FastAPICache.init(InMemoryBackend())

    yield

    await client.stop()
    FastAPICache.reset()


app = FastAPI(
    debug=AppConfig.DEBUG,
    title=AppConfig.NAME,
    description=AppConfig.DESCRIPTION,
    version=AppConfig.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    middleware=[
        Middleware(RequestLoggerMiddleware, ignore_paths=["/", "/health/", "/docs", "/redoc", "/openapi.json"]),
        Middleware(SessionMiddleware),
        Middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["*"],
                   allow_headers=["*"],
                   allow_credentials=True),
    ],
    exception_handlers={
        HTTPError: GlobalExceptionHandlerMiddleware(),
    },
    lifespan=app_lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Re-raise so we can handle in exception middleware
    formatted_errors = format_validation_error(exc.errors())

    raise ValidationError("Pydantic Validation Error", detail=formatted_errors)


for router in routers.__all__:
    app.include_router(**getattr(routers, router).__dict__)


@app.get("/")
def index():
    return f"{AppConfig.NAME} v{AppConfig.VERSION}"


@app.get("/health")
async def health():
    return {"message": "healthy"}
