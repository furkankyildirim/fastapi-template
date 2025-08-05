from http import HTTPStatus

from src.utils import Error


class HTTPError(Error):
    status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR


class ServiceError(HTTPError):
    """Exception raised from service calls"""
    status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    message = "Service Error"


class ValidationError(HTTPError):
    """Exception raised from request validations"""
    status_code: HTTPStatus = HTTPStatus.UNPROCESSABLE_ENTITY
    message = "Validation Error"


class AuthorizationError(HTTPError):
    """Exception raised from authorization errors"""
    status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED
    message = "Authorization Error"


class ForbiddenError(HTTPError):
    """Exception raised from forbidden errors"""
    status_code: HTTPStatus = HTTPStatus.FORBIDDEN
    message = "Forbidden Error"


class BadRequestError(HTTPError):
    """Exception raised from bad request errors"""
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST
    message = "Bad Request Error"


class NotFoundError(HTTPError):
    """Exception raised from not found errors"""
    status_code: HTTPStatus = HTTPStatus.NOT_FOUND
    message = "Not Found Error"


class MethodNotAllowedError(HTTPError):
    """Exception raised from method not allowed errors"""
    status_code: HTTPStatus = HTTPStatus.METHOD_NOT_ALLOWED
    message = "Method Not Allowed Error"


class TooManyRequestsError(HTTPError):
    """Exception raised from too many requests errors"""
    status_code: HTTPStatus = HTTPStatus.TOO_MANY_REQUESTS
    message = "Too Many Requests Error"
