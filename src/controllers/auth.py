from typing import Annotated

from fastapi import APIRouter, Query, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm

from src import AppConfig
from src.services import AuthService
from src.models import TokenRequestModel, TokenResponseModel, RefreshTokenModel, UserModel, UserCreateModel


class AuthController:
    router = APIRouter(include_in_schema=AppConfig.DEBUG)
    tags = ['Authentication']

    @staticmethod
    @router.post(
        "/login",
        response_model=dict,
        summary="Login Form",
        response_model_by_alias=True,
        tags=tags,
    )
    async def login(request: OAuth2PasswordRequestForm = Depends()) -> dict:
        """
        Login Form Endpoint:

        Args:
            request (OAuth2PasswordRequestForm): OAuth2PasswordRequestForm.

        Returns:
            dict: dict.
        """
        return AuthService.login(request=request)

    @staticmethod
    @router.post(
        "/register",
        response_model=UserModel,
        summary="Create User",
        response_model_by_alias=True,
        tags=tags)
    async def create_user(
            user: UserCreateModel,
    ) -> UserModel:
        """
        Create user:

        Args:
            user (UserCreateModel): User create model.

        Returns:
            UserModel: User model.
        """
        return await AuthService.create_user(user=user)

    @staticmethod
    @router.post(
        "/token",
        response_model=TokenResponseModel,
        summary="Token",
        response_model_by_alias=True,
        tags=tags,
    )
    async def token(
            request: Annotated[TokenRequestModel, Body]
    ) -> TokenResponseModel:
        """
        Token Endpoint:

        Args:
            request (Annotated[TokenRequestModel, Body]): Token request model.

        Returns:
            TokenResponseModel: Token response model.
        """
        return AuthService.create_token(request=request)

    @staticmethod
    @router.post(
        "/refresh",
        response_model=TokenResponseModel,
        summary="Refresh",
        tags=tags,
    )
    async def refresh(
            refresh: Annotated[RefreshTokenModel, Body]
    ) -> TokenResponseModel:
        """
        Refresh Endpoint:

        Args:
            refresh (Annotated[RefreshTokenModel, Body]): Refresh token model.

        Returns:
            TokenResponseModel: Token response model.
        """
        return AuthService.refresh_token(payload=refresh)

    @staticmethod
    @router.post(
        "/activate",
        response_model=bool,
        summary="Send Activation Email",
        tags=tags,
    )
    async def send_activation_email(
            current_user: Annotated[UserModel, Depends(AuthService.get_current_user)]
    ) -> bool:
        """
        Send Activation Email Endpoint:

        Args:
            current_user (Annotated[UserModel, Depends(AuthService.get_current_user)]): Current user.

        Returns:
            bool: True if email is sent, False otherwise.
        """
        return await AuthService.send_activation_email(user=current_user)

    @staticmethod
    @router.get(
        "/activate/{token}",
        response_model=bool,
        summary="Activate User",
        tags=tags,
    )
    async def activate_user(token: str) -> bool:
        """
        Activate User Endpoint:

        Args:
            token (str): Token.

        Returns:
            bool: True if user is activated, False otherwise.
        """
        return await AuthService.activate_user(token=token)

    @staticmethod
    @router.post(
        "/reset-password",
        response_model=bool,
        summary="Send Reset Password Email",
        tags=tags,
    )
    async def send_reset_password_email(
            email: str
    ) -> bool:
        """
        Send Reset Password Email Endpoint:

        Args:
            email (str): Email.

        Returns:
            bool: True if email is sent, False otherwise.
        """
        return await AuthService.send_reset_password_email(email=email)

    @staticmethod
    @router.get(
        "/reset-password/{token}",
        response_model=str,
        summary="Reset Password",
        tags=tags,
    )
    async def reset_password(token: str) -> str:
        """
        Reset Password Endpoint:

        Args:
            token (str): Token.

        Returns:
            str: Token.
        """
        return await AuthService.reset_password(token=token)

    @staticmethod
    @router.post(
        "/reset-password/change",
        response_model=bool,
        summary="Reset Password with Token",
        tags=tags,
    )
    async def change_password_with_token(
            token: str,
            password: str
    ) -> bool:
        """
        Change Password with Token Endpoint:

        Args:
            token (str): Token.
            password (str): Password.

        Returns:
            bool: True if password is changed, False otherwise.
        """
        return await AuthService.change_password_with_token(token=token, password=password)

    @staticmethod
    @router.get(
        "/google/login",
        summary="Google Login",
        tags=tags,
    )
    def google_login():
        """
        Google Login Endpoint:
        """
        return AuthService.google_login()

    @staticmethod
    @router.get(
        "/google/register",
        summary="Google Register",
        tags=tags,
    )
    def google_register():
        """
        Google Register Endpoint:
        """
        return AuthService.google_register()

    @staticmethod
    @router.get(
        "/google/callback-login",
        response_model=TokenResponseModel,
        summary="Google Callback",
        tags=tags,
        include_in_schema=False,
    )
    async def google_callback(code: Annotated[str, Query(...)]):
        """
        Google Callback Endpoint:

        Args:
            code (str): Code.

        Returns:
            dict: dict.
        """
        return await AuthService.google_callback_login(code=code)

    @staticmethod
    @router.get(
        "/google/callback-register",
        summary="Google Callback Register",
        response_model=UserModel,
        tags=tags,
        include_in_schema=False,
    )
    async def google_callback_register(code: Annotated[str, Query(...)]):
        """
        Google Callback Register Endpoint:

        Args:
            code (str): Code.

        Returns:
            dict: dict.
        """
        return await AuthService.google_callback_register(code=code)
