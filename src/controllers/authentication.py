from typing import Any, Dict
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.common import Response
from src.schemas import TokenSchema, LoginSchema, RegistrationSchema
from src.services import AuthenticationService


class AuthenticationController:
    router = APIRouter()
    tags = ['Authentication']

    @staticmethod
    @router.post(
        "/login",
        response_model=Response[Any],
        summary="Login",
        response_model_by_alias=False,
        tags=tags,
    )
    def login(request: LoginSchema) -> Response[TokenSchema]:
        """
        Login:
        - **request** (Login): Login schema.
        """
        return AuthenticationService.login(request=request)

    @staticmethod
    @router.post(
        "/login-form",
        response_model=Dict,
        summary="Login Form",
        response_model_by_alias=False,
        tags=tags,
    )
    def login_form(request: OAuth2PasswordRequestForm = Depends()) -> Dict:
        """
        Login:
        - **request** (Login): Login schema.
        """
        return AuthenticationService.login_form(request=request)

    @staticmethod
    @router.post(
        "/register",
        response_model=Response[Any],
        summary="Registration",
        response_model_by_alias=False,
        tags=tags,
    )
    def register(request: RegistrationSchema) -> Response[Any]:
        """
        Registration:
        - **request** (Registration): Registration schema.
        """
        return AuthenticationService.register(request=request)
