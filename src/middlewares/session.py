from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.database.connections import postgres_session


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            # Begin a new transaction if one isn't already in progress
            if not postgres_session.in_transaction():
                postgres_session.begin()
            # If there's a transaction but it's not active, rollback and begin new
            elif not postgres_session.is_active:
                postgres_session.rollback()
                postgres_session.begin()

            response = await call_next(request)
            return response

        except Exception as e:
            postgres_session.rollback()
            raise e 