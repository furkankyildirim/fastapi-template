import uuid

from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from loguru import logger

from typing import List
import json
from src.utils.http import request_id_trace_context

REQUEST_ID_KEY_NAME = "requestid"


class RequestLoggerMiddleware:
    """
        Middleware to log request and response data.

        Args:
            app (ASGIApp): ASGI application
            ignore_paths (List): List of route paths to ignore on logging
    """

    def __init__(self, app: ASGIApp, ignore_paths: List[str] = None) -> None:
        self.app = app
        if ignore_paths:
            # Remove trailing slashes to prevent logging http redirects
            self.ignore_paths = list(map(lambda path: path.rstrip('/'), ignore_paths))
        else:
            self.ignore_paths = []

        logger.add("/logs/file.log", serialize=False,
                   # format should be in json format {"time": "time", "level": "level", "message": "message", "extra": "extra"}
                   format='{{"time": "{time}", "level": "{level}", "message": "{message}", "extra": {extra}}}')

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:

        # Only intercept if asgi channel scope is http
        if scope["type"] == "http":
            # Use custom responder to intercept before body is rendered to bytes.
            responder = _RequestLoggingResponder(self.app, ignore_paths=self.ignore_paths)
            await responder(scope, receive, send)
        else:
            await self.app(scope, receive, send)


class _RequestLoggingResponder:
    """
        Asgi Responder with custom receive and send channels to log before messages are processed

        Args:
            app (ASGIApp): ASGI application
            ignore_paths (List): List of route paths to ignore on logging
    """

    def __init__(self, app: ASGIApp, ignore_paths: List[str]) -> None:
        self.app = app
        self.receive: Receive
        self.send: Send
        self._path: str = ""
        self._method: str = ""
        self._request_headers = None
        self._request_body: bytearray = bytearray()
        self._response_body: bytearray = bytearray()
        self._response_headers = None
        self._response_status_code = None
        self.can_log = True
        self.ignore_paths = ignore_paths
        self._context_log = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:

        # Store asgi default receive and send channels to use internally
        self.receive = receive
        self.send = send

        request = Request(scope)
        self._method = request.method
        self._path = request.url.path
        headers = Headers(scope=scope)

        # Store request headers for logging
        self._request_headers = headers

        # Check ignored paths
        self.can_log = self._path.rstrip('/') not in self.ignore_paths
        self._collect_log_traces()

        # Process request with custom receive and log functions
        with logger.contextualize(**self._context_log):
            await self.app(scope, self.receive_with_logging, self.send_with_logging)

            # Log stored request and response data
            if self.can_log and self._method != "GET":
                self._safe_log_request_response()

    def _get_request_id(self) -> str:
        """
        Checks request header, if exist it returns requestid value, else generate a new value.
        Returns:
            (str): request id
        """
        if REQUEST_ID_KEY_NAME in self._request_headers:
            request_id = self._request_headers[REQUEST_ID_KEY_NAME]
        else:
            request_id = str(uuid.uuid4())

        return request_id

    def _collect_log_traces(self) -> None:
        """
        Check requestid in header, newrelic and sentry trace ids. If exist, it will bind to logger.
        And function set requestid value to context for attach to request headers.
        """
        # Adding request id that provided from backend team requests, to context dict
        request_id = self._get_request_id()
        request_id_trace_context.set(request_id)
        self._context_log.update({
            "request_id": request_id,
        })

    async def receive_with_logging(self) -> Message:
        """
            Asgi receive channel with log handling.
            Stores request body in self

            Returns:
                Message : Asgi Message object to send to channels
        """
        message = await self.receive()

        if message["type"] != "http.request":
            return message

        # If request is not suitable for logging return immediately
        if not self.can_log:
            return message

        # Store request body for logging
        body: bytes = message.get("body", b"")
        self._request_body.extend(body)

        return message

    async def send_with_logging(self, message: Message) -> None:
        """
            Asgi send channel with log handler
        """
        # Store headers and set can_log before actual processing of response
        if message["type"] == "http.response.start":
            self._response_status_code = message.get("status")
            headers = Headers(raw=message["headers"])

            # Store response headers for logging
            self._response_headers = headers

            # Only log json output
            self.can_log = self.can_log and "application/json" in headers.get("content-type", "")

        # Store body before actual processing of body
        elif message["type"] == "http.response.body":
            if self.can_log:
                body: bytes = message.get("body", b"")

                # Store response body for logging
                self._response_body.extend(body)

        await self.send(message)

    def _safe_log_request_response(self):
        """
            Logs collected request and response data
        """

        # Wrap with a global catch to not cause data loss during logging
        try:
            request_method = self._method
            request_body = self._request_body and json.loads(self._request_body)
            response_body = self._response_body and json.loads(self._response_body)
            request_headers = self._request_headers and dict(self._request_headers.items())
            response_headers = self._response_headers and dict(self._response_headers.items())

            # bind request and response to "extra" field in log json
            logger.bind(
                request={
                    "method": request_method,
                    "headers": request_headers,
                    "body": request_body,
                    "path": self._path,
                }, response={
                    "headers": response_headers,
                    "body": response_body,
                    "status_code": self._response_status_code,
                },
            ).info(f"Response Sent: {self._path}")
        except Exception as e:
            pass
