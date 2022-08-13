from os import environ as env
from typing import Union
from http import HTTPStatus

from fastapi import FastAPI, HTTPException, encoders,Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


from .configs import AppConfig
from . import routers

app = FastAPI(
    debug=AppConfig.DEBUG,
    title=AppConfig.NAME,
    description=AppConfig.DESCRIPTION,
    version=env.get("APP_VERSION", "1.0.0"),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    body = encoders.jsonable_encoder(exc)
    detail = body['detail']

    message = detail["message"] if "message" in detail else "Something went wrong"

    return JSONResponse({"message": message, "isSuccess": False}, 
                        status_code=body['status_code'])


if not AppConfig.DEBUG:
    @app.middleware("http")
    async def exception_handling(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            return JSONResponse({"message": "Server Error: {} {}".format(type(exc).__name__, str(exc)), "isSuccess": False}, 
                                status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler2(request, exc):
    error_list = exc.errors()
    if error_list:
        return JSONResponse(
            content=encoders.jsonable_encoder({"message": "{} {}".format(error_list[0]['loc'][1], "field is required"),
            "isSuccess": False, }), status_code=HTTPStatus.UNPROCESSABLE_ENTITY)


for router in routers.__all__:
    app.include_router(**getattr(routers, router).__dict__)


@app.get("/")
def index():
    return f"{app.title} v{app.version}"


@app.get("/health")
async def health():
    return {"message": "healthy"}
