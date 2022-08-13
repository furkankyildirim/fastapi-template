from fastapi import HTTPException
from http import HTTPStatus


class AUTHORIZATION_ERROR(HTTPException):
    def __init__(self, message: str = "Authorization Error") -> None:
        super().__init__(status_code=HTTPStatus.UNAUTHORIZED,
                         detail={"message": message, "isSuccess": False},
                         headers={"WWW-Authenticate": "Bearer"})


class NOT_FOUND_ERROR(HTTPException):
    def __init__(self, message: str = "Not Found Error") -> None:
        super().__init__(status_code=HTTPStatus.FORBIDDEN,
                         detail={"message": message, "isSuccess": False})


class BAD_REQUEST_ERROR(HTTPException):
    def __init__(self, message: str = "Bad Request Error") -> None:
        super().__init__(status_code=HTTPStatus.BAD_REQUEST,
                         detail={"message": message, "isSuccess": False})


class METHOD_NOT_ALLOWED_ERROR(HTTPException):
    def __init__(self, message: str = "Method Not Allowed Error") -> None:
        super().__init__(status_code=HTTPStatus.METHOD_NOT_ALLOWED,
                         detail={"message": message, "isSuccess": False})
