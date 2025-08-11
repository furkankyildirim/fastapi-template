import secrets
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated, Dict

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_cache.decorator import cache
from starlette.responses import RedirectResponse

from src.configs import AppConfig, ServiceCallerConfig
from src.database.user import UserDatabase
from src.database.token import TokenDatabase
from src.errors import AuthorizationError, BadRequestError
from src.models import (TokenRequestModel, TokenResponseModel, UserModel, RefreshTokenModel,
                        UserCreateModel, TokenCreateModel, TokenType)
from src.utils import SecurityUtils
from src.utils.validation import ValidationUtils

from .oauth import OAuthService
from .aws import SimpleEmailService


class AuthService:
    @staticmethod
    def create_token(request: TokenRequestModel) -> TokenResponseModel:
        """
        Login service:

        Args:
            request (TokenRequestModel): Token request model.

        Returns:
            TokenSchema: Token schema.
        """

        user: UserModel = AuthService._authenticate_user(email=request.email, password=request.password)
        token_schema: TokenResponseModel = AuthService._generate_token(text=user.id)

        return token_schema

    @staticmethod
    def refresh_token(payload: RefreshTokenModel) -> TokenResponseModel:
        """
        Refresh token:

        Args:
            payload (RefreshTokenModel): Refresh token model

        Returns:
            TokenSchema: Token schema.
        """

        user_id: str = AuthService._validate_token(token=payload.refresh)
        token_schema: TokenResponseModel = AuthService._generate_token(text=user_id)

        return token_schema

    @staticmethod
    def login(request: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
        """
        Login:

        Args:
            request (Annotated[OAuth2PasswordRequestForm, Depends()]): Form data.

        Returns:
            dict: Token response.
        """

        user: UserModel = AuthService._authenticate_user(email=request.username, password=request.password)
        token_schema: TokenResponseModel = AuthService._generate_token(text=user.id)

        response: Dict = {"access_token": token_schema.access,
                          "token_type": "bearer",
                          "response": {"status_code": HTTPStatus.OK}}

        return response

    @staticmethod
    async def create_user(user: UserCreateModel, is_google: bool = False) -> UserModel:
        """
        Create user:

        Args:
            user (UserCreateModel): User create model.
            is_google (bool): True if user is created from Google.

        Returns:
            UserModel: User model.

        Raises:
            ValidationError: If invalid email.
            BadRequestError: If email already exists.
            BadRequestError: If password doesn't meet strength requirements.
            BadRequestError: If could not create user.
        """
        # Validate email and check uniqueness with improved Gmail handling
        ValidationUtils.validate_email(email=user.email)

        # Validate password strength for non-Google accounts
        if not is_google:
            ValidationUtils.validate_password(password=user.password)

        # Hash the password
        user.password = SecurityUtils.bcrypt(text=user.password)

        try:
            user = UserDatabase.create_user(user=user)
        except Exception as e:
            raise BadRequestError(message="Could not create user", caught_exception=e)

        if not is_google:
            await AuthService.send_activation_email(user=user)
        else:
            user.is_active = True
            UserDatabase.update_user(user_id=user.id, user=user)

        return user

    @staticmethod
    def google_login() -> RedirectResponse:
        """
        Google login:

        Returns:
            RedirectResponse: Redirect to Google OAuth2 login URL.
        """
        redirect_url = ServiceCallerConfig.Google.REDIRECT_LOGIN_URI

        url = OAuthService.get_google_auth_url(redirect_uri=redirect_url)
        return RedirectResponse(url=url)

    @staticmethod
    def google_register() -> RedirectResponse:
        """
        Google register:

        Returns:
            RedirectResponse: Redirect to Google OAuth2 register URL.
        """
        redirect_url = ServiceCallerConfig.Google.REDIRECT_REGISTER_URI

        url = OAuthService.get_google_auth_url(redirect_uri=redirect_url)
        return RedirectResponse(url=url)

    @staticmethod
    async def google_callback_login(code: str) -> TokenResponseModel:
        """
        Google callback:

        Args:
            code (str): Authorization code.

        Returns:
            TokenResponseModel: Token response.
        """

        if not code:
            raise BadRequestError(message="Authorization code not provided")

        redirect_uri = ServiceCallerConfig.Google.REDIRECT_LOGIN_URI

        token_data = await OAuthService.call_google_auth_service(code=code, redirect_uri=redirect_uri)
        access_token = token_data.get("access_token")

        if not access_token:
            raise BadRequestError(message="Invalid access token")

        user_info = await OAuthService.call_google_user_service(token=access_token)
        db_user = UserDatabase.get_user_by_email(user_info.get("email"))

        if not db_user:
            raise AuthorizationError(message="Invalid credentials")

        token_schema: TokenResponseModel = AuthService._generate_token(text=db_user.id)
        return token_schema

    @staticmethod
    async def google_callback_register(code: str) -> UserModel:
        """
        Google callback:

        Args:
            code (str): Authorization code.

        Returns:

        """

        if not code:
            raise BadRequestError(message="Authorization code not provided")

        redirect_uri = ServiceCallerConfig.Google.REDIRECT_REGISTER_URI

        token_data = await OAuthService.call_google_auth_service(code=code, redirect_uri=redirect_uri)
        access_token = token_data.get("access_token")

        if not access_token:
            raise BadRequestError(message="Invalid access token")

        user_info = await OAuthService.call_google_user_service(token=access_token)

        new_user = {
            "email": user_info.get("email"),
            "name": user_info.get("given_name"),
            "surname": user_info.get("family_name"),
            "role": "user",
            "subscription": "free",
            "password": secrets.token_urlsafe(16)
        }

        new_user = await AuthService.create_user(user=UserCreateModel.model_validate(new_user), is_google=True)
        return new_user

    @staticmethod
    @cache(expire=30)
    def get_current_user(token: Annotated[str, Depends(SecurityUtils.oauth2_scheme)]) -> UserModel:
        """
        Gets current user

        Args:
            token (Annotated[str, Depends(Hash.oauth2_scheme)]): Access token.

        Returns:
            UserSchema: User schema.
        """

        user_id: str = AuthService._validate_token(token=token)
        user: UserModel = AuthService._get_user_by_id(user_id=user_id)

        if not user.is_activated:
            raise AuthorizationError(message="User is not active.")

        return user

    @staticmethod
    async def send_activation_email(user: UserModel) -> bool:
        """
        Send account activation link:

        Args:
            user (UserModel): User model.

        Returns:
            bool: True if successful.
        """

        if user.is_active is not None:
            raise AuthorizationError(message="User is already active")

        token = secrets.token_urlsafe(16)
        link = f"{AppConfig.URL}/auth/activate/{token}"
        expires_at = datetime.now() + timedelta(hours=24)

        token_data = TokenCreateModel(
            token=token,
            token_type=TokenType.ACTIVATION,
            expires_at=expires_at
        )

        TokenDatabase.create_token(user_id=user.id, token_data=token_data)
        SimpleEmailService.send_activate_account_link(recipient=user.email, name=user.name, link=link)

        return True

    @staticmethod
    async def activate_user(token: str) -> bool:
        """
        Validate activation link:

        Args:
            token (str): Token.

        Returns:
            bool: True if valid.
        """
        db_token = TokenDatabase.get_valid_token(token=token, token_type=TokenType.ACTIVATION)
        if not db_token:
            raise AuthorizationError(message="Invalid or expired link")

        try:
            user = UserDatabase.get_user(user_id=db_token.user_id)
            user.is_active = True
            UserDatabase.update_user(user=user, user_id=user.id)

            TokenDatabase.mark_token_as_used(token=token)

            return True
        except Exception as e:
            raise BadRequestError(message="Could not activate user", caught_exception=e)

    @staticmethod
    async def send_reset_password_email(email: str) -> bool:
        """
        Send reset password email:

        Args:
            email (str): Email.

        Returns:
            bool: True if successful.
        """
        user = UserDatabase.get_user_by_email(email=email)
        if not user:
            raise AuthorizationError(message="Invalid email")

        token = secrets.token_urlsafe(16)
        link = f"{AppConfig.URL}/auth/reset-password/{token}"
        expires_at = datetime.now() + timedelta(hours=24)

        token_data = TokenCreateModel(
            token=token,
            token_type=TokenType.RESET_PASSWORD,
            expires_at=expires_at
        )

        TokenDatabase.create_token(user_id=user.id, token_data=token_data)
        SimpleEmailService.send_reset_password_link(recipient=user.email, name=user.name, link=link)

        return True

    @staticmethod
    async def reset_password(token: str) -> str:
        """
        Reset password:

        Args:
            token (str): Token.

        Returns:
            str: Token.
        """
        db_token = TokenDatabase.get_valid_token(token=token, token_type=TokenType.RESET_PASSWORD)
        if not db_token:
            raise AuthorizationError(message="Invalid or expired link")

        return token

    @staticmethod
    async def change_password_with_token(token: str, password: str) -> bool:
        """
        Change password:

        Args:
            token (str): Token.
            password (str): Password.

        Returns:
            bool: True if successful.
        """
        db_token = TokenDatabase.get_valid_token(token=token, token_type=TokenType.RESET_PASSWORD)
        if not db_token:
            raise AuthorizationError(message="Invalid or expired link")

        try:
            user = UserDatabase.get_user(user_id=db_token.user_id)

            user.password = SecurityUtils.bcrypt(text=password)
            UserDatabase.update_user(user=user, user_id=user.id)

            TokenDatabase.mark_token_as_used(token=token)

            return True

        except Exception as e:
            raise BadRequestError(message="Could not change password", caught_exception=e)

    @staticmethod
    def _authenticate_user(email: str, password: str) -> UserModel:
        """
        Authenticates user:

        Args:
            email (str): Email.
            password (str): Password.

        Returns:
            UserAuthModel: User model.
        """
        user = UserDatabase.get_user_by_email(email=email)

        if not user:
            raise AuthorizationError(message="Invalid credentials")

        if not SecurityUtils.verify(plain_password=password, hashed_password=user.password):
            raise AuthorizationError(message="Invalid credentials")

        if not user.is_activated:
            raise AuthorizationError(message="User is not active")

        return user

    @staticmethod
    def _get_user_by_id(user_id: str) -> UserModel:
        """
        Gets user by user ID:

        Args:
            user_id (str): User ID.

        Returns:
            UserSchema: User schema.
        """
        try:
            user: UserModel = UserDatabase.get_user(user_id=user_id)
            if not user:
                raise AuthorizationError(message="Could not validate token")
            return user
        except Exception as e:
            raise AuthorizationError(message="Could not validate token")

    @staticmethod
    def _generate_token(text: str) -> TokenResponseModel:
        """
        Create access token:

        Args:
            text (str): Text to be encoded.

        Returns:
            TokenSchema: Token schema.
        """
        token: TokenResponseModel = TokenResponseModel.model_validate(
            SecurityUtils.generate_token(text=text))
        return token

    @staticmethod
    def _validate_token(token: str) -> str:
        """
        Validates token and returns user_id:

        Args:
            token (str): Access token.

        Returns:
            str: User ID.
        """
        try:
            user_id: str = SecurityUtils.decode_token(token=token)
            if not user_id:
                raise AuthorizationError(message="Could not validate token for login.")

            return user_id

        except Exception as e:
            raise AuthorizationError(message="Could not validate token for login.")
