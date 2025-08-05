from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from src.configs.app import AppConfig
from src.utils import Error


class GlobalExceptionHandlerMiddleware:
    def __init__(self, app: FastAPI = None):
        self.app = app

    async def __call__(self, request: Request, exc: Exception):
        return await self.handle_exception(request, exc)

    async def handle_exception(self, request: Request, exc: Exception):
        message = "Unexpected error occurred."
        detail = ""
        caught_exception = None

        if isinstance(exc, Error):
            message = getattr(exc, 'message', message)
            detail = getattr(exc, 'detail', detail)
            caught_exception = getattr(exc, 'caught_exception', caught_exception)

        logger.bind(
            request={
                "method": request.method,
                "path": request.url.path,
                "headers": dict(request.headers),
                "query_params": dict(request.query_params),
                # "body": (await request.body()).decode("utf-8"),  # Handle request body
            }
        ).error(message)

        content = {"message": message}

        if AppConfig.DEBUG:
            content["detail"] = detail
            content["caught_exception"] = str(caught_exception)

        return JSONResponse(
            status_code=getattr(exc, "status_code", 500),
            content=content,
        )
