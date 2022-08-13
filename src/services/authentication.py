from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from http import HTTPStatus
from typing import Any, Dict

from src.database import UserDatabase
from src.errors import AUTHORIZATION_ERROR
from src.schemas import LoginSchema, TokenSchema, RegistrationSchema
from src.schemas.common import Response
from src.schemas.user import UserSchema
from src.utils import Hash, ImageUtils

from .user import UserService


class AuthenticationService:
    @staticmethod
    def login(request: LoginSchema) -> Response[TokenSchema]:
        """
        Login:
        - **request** (Login): Login schema.
        """

        user: UserSchema = AuthenticationService.__validate_user(credential=request.email, password=request.password)
        token: TokenSchema = AuthenticationService.__generate_token(text=user.id)
        response: Response[TokenSchema] = Response(message="Login is successfull", isSuccess=True, data=token)
        return response

    @staticmethod
    def login_form(request: OAuth2PasswordRequestForm) -> Dict:
        """
        Login Form:
        - **request** (Login): Login schema.
        """

        user: UserSchema = AuthenticationService.__validate_user(credential=request.username, password=request.password)
        token_field: TokenSchema = AuthenticationService.__generate_token(text=user.id)
        response: Dict = {"access_token": token_field.token,
                          "token_type": "bearer",
                          "response": {"status_code": HTTPStatus.OK}}

        return response

    @staticmethod
    def get_current_user(token: str = Depends(Hash.reusable_oauth2)) -> UserSchema:
        """
        Get Current User:
        - **access_token** (str): Access token.
        """

        user_id: str = AuthenticationService.__get_user_id_from_token(token=token)
        user: UserSchema = AuthenticationService.__get_user_by_id(user_id=user_id)

        user.profile_photo: str = ImageUtils.get_image_url_from_prefix(prefix=user.profile_photo)

        return user

    @staticmethod
    def register(request: RegistrationSchema) -> Response[Any]:
        """
        Register:
        - **request** (RegistrationSchema): RegistrationSchema schema.
        """

        user_id: str = AuthenticationService.__generate_user_id()
        password: str = AuthenticationService.__encrypt_password(password=request.password)

        filename: str = ImageUtils.get_default_image()
        profile_photo: str = ImageUtils.get_image_with_prefix(
            filename=filename, prefix="user/profile-photo")

        user: UserSchema = UserSchema(
            id=user_id,
            name=request.name,
            username=request.username,
            email=request.email,
            password=password,
            profile_photo=profile_photo,
        )

        response = UserService.create_user(user=user)
        return response

    @staticmethod
    def __get_user_id_from_token(token: str) -> str:
        """
        Get User ID from Token:
        - **access_token** (str): Access token.
        """
        try:
            user_id: str = Hash.decode_token(token=token)

            if not user_id:
                raise AUTHORIZATION_ERROR(message="Could not validate token for login.")

            return user_id

        except Exception as e:
            raise AUTHORIZATION_ERROR(message="Could not validate token for login.")

    @staticmethod
    def __get_email_from_token(token: str) -> str:
        """
        Get Email from Token:
        - **access_token** (str): Access token.
        """
        try:
            email: str = Hash.decode_token(token=token)

            if not email:
                raise AUTHORIZATION_ERROR(message="Could not validate token for registration.")

            return email

        except Exception as e:
            raise AUTHORIZATION_ERROR(message="Could not validate token for registration.")

    @staticmethod
    def __get_user_by_id(user_id: str) -> UserSchema:
        """
        Get User by ID:
        - **user_id** (str): User ID.
        """
        user: UserSchema = UserDatabase.get_user(user_id=user_id)
        if not user:
            raise AUTHORIZATION_ERROR(message="Could not validate token for registration")
        return user

    @staticmethod
    def __validate_user(credential: str, password: str) -> UserSchema:
        """
        Validate user from email and password:
        - **request** (Login): Login schema.
        """
        user: UserSchema = UserDatabase.get_user_by_email(email=credential)

        if not user or not Hash.verify(user.password, password):
            raise AUTHORIZATION_ERROR(message="Invalid Credentials")

        return user

    @staticmethod
    def __generate_token(text: str) -> TokenSchema:
        """
        Create token:
        - **text** (str): Text.
        """
        token: TokenSchema = TokenSchema(token=Hash.generate_token(text))
        return token

    @staticmethod
    def __generate_user_id() -> str:
        """
        Generate user ID:
        """
        user_id: str = Hash.id_generator()
        return user_id

    @staticmethod
    def __encrypt_password(password: str) -> str:
        """
        Encrypt password:
        - **password** (str): Password.
        """
        password: str = Hash.bcrypt(password)
        return password
