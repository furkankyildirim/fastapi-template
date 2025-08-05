from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from src.utils.http import client
from src.errors.generic import ValidationError, HTTPError

from src.configs import AppConfig
from . import routers
from src.middlewares import GlobalExceptionHandlerMiddleware, RequestLoggerMiddleware, SessionMiddleware
# from .database.connections import RedisConnection
from .utils.common import format_validation_error

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
    }
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Re-raise so we can handle in exception middleware
    formatted_errors = format_validation_error(exc.errors())

    raise ValidationError("Pydantic Validation Error", detail=formatted_errors)


@app.on_event("startup")
async def startup():
    await client.start()
    # await RedisConnection.connect()


@app.on_event("shutdown")
async def shutdown():
    await client.stop()
    # await RedisConnection.disconnect()

for router in routers.__all__:
    app.include_router(**getattr(routers, router).__dict__)


@app.get("/")
def index():
    return f"{AppConfig.NAME} v{AppConfig.VERSION}"


@app.get("/health")
async def health():
    return {"message": "healthy"}
