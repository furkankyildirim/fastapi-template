import sys
import types
from http import HTTPStatus
from typing import Union, List

from src.utils.common import json_serializer


class Error(Exception):
    message: str = "Unexpected error occurred."
    status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str = None, *, detail: dict = None, caught_exception: Exception = None) -> None:
        if message is not None:
            self.message = message
        if detail is not None:
            self.detail = detail
        else:
            self.detail = {}
        self.caught_exception = caught_exception or sys.exc_info()[1]

    @property
    def __dict__(self):
        """
        Dict representation of the error class. Return value will be appended to log data.

        Returns:
            Dict: Dict containing stringified detail and caught exception information if any.
        """
        detail = self.detail or ''
        caught_exception: dict = {}

        if self.caught_exception:
            caught_exception["name"] = getattr(type(self.caught_exception), '__name__', '')
            caught_exception["repr"] = getattr(self.caught_exception, '__repr__', lambda x: '')()

        return {
            "detail": detail,
            "caught_exception": caught_exception
        }

    def __str__(self):
        return json_serializer({"message": self.message, **self.__dict__})

    def with_current_traceback(self, ignored_packages: Union[List, None] = None):
        """
            Returns self with full traceback till executed
        Args:
            ignored_packages(list): Ignores given packages from traceback.

        Returns: (Error) Self with traceback

        """

        tb = None

        if ignored_packages is None:
            ignored_packages = ['fastapi.', 'starlette.', 'uvicorn.', 'multiprocessing.', 'asyncio.',
                                'algo_utils.error']

        frame = sys._getframe()

        # Loop until start of execution
        while frame is not None:
            try:
                # Ignore irrelevant modules
                module = frame.f_globals["__name__"]
                if any(module.startswith(ignored) for ignored in ignored_packages):
                    frame = frame.f_back
                    continue
            except (AttributeError, KeyError):
                pass

            # create trace on each step
            tb = types.TracebackType(tb, frame, frame.f_lasti, frame.f_lineno)
            frame = frame.f_back

        return self.with_traceback(tb)
