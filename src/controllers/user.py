from typing import Annotated

from fastapi import APIRouter, Query, Depends, Body

from src import AppConfig
from src.models import (UserModel, UserEditInfoModel, UserEditEmailModel, UserEditPasswordModel)
from src.services import UserService, AuthService


class UserController:
    router = APIRouter(include_in_schema=AppConfig.DEBUG)
    tags = ['Users']

    @staticmethod
    @router.get(
        "",
        response_model=UserModel,
        summary="Get User by ID",
        response_model_by_alias=True,
        tags=tags,
    )
    async def get_user(
            user_id: Annotated[str, Query(alias="id")],
            current_user: Annotated[UserModel, Depends(AuthService.get_current_user)]
    ):
        """
        Get user from user id:

        Args:
            user_id (str): User ID.
            current_user (Annotated[UserModel, Depends(AuthService.get_current_user)]): Current user.

        Returns:
            UserModel: User model.
        """
        return UserService.get_user(current_user=current_user, user_id=user_id)

    @staticmethod
    @router.get(
        "/me",
        response_model=UserModel,
        summary="Get Current User",
        response_model_by_alias=True,
        tags=tags,
    )
    async def get_current_user(
            current_user: Annotated[UserModel, Depends(AuthService.get_current_user)]
    ):
        """
        Get current user:

        Args:
            current_user (Annotated[UserModel, Depends(AuthService.get_current_user)]): Current user.

        Returns:
            UserModel: User model.
        """
        return current_user

    @staticmethod
    @router.post(
        "/edit/info",
        response_model=UserModel,
        summary="Update User Info",
        response_model_by_alias=True,
        tags=tags,
    )
    async def update_user_info(
            data: Annotated[UserEditInfoModel, Body(...)],
            current_user: Annotated[UserModel, Depends(AuthService.get_current_user)]
    ) -> UserModel:
        """
        Update user's first name and last name.
        
        Args:
            data (UserEditInfoModel): Updated user information.
            current_user (Annotated[UserModel, Depends(AuthService.get_current_user)]): Current user.
        
        Returns:
            UserModel: Updated user model.
        """
        return UserService.update_user_info(current_user=current_user, data=data)

    @staticmethod
    @router.post(
        "/edit/email",
        response_model=UserModel,
        summary="Update User Email",
        response_model_by_alias=True,
        tags=tags,
    )
    async def update_user_email(
            data: Annotated[UserEditEmailModel, Body(...)],
            current_user: Annotated[UserModel, Depends(AuthService.get_current_user)]
    ) -> UserModel:
        """
        Update user's email address.
        
        Args:
            data (UserEditEmailModel): Updated email information.
            current_user (Annotated[UserModel, Depends(AuthService.get_current_user)]): Current user.
        
        Returns:
            UserModel: Updated user model.
        """
        return await UserService.update_user_email(current_user=current_user, data=data)

    @staticmethod
    @router.post(
        "/edit/password",
        response_model=UserModel,
        summary="Update User Password",
        response_model_by_alias=True,
        tags=tags,
    )
    async def update_user_password(
            data: Annotated[UserEditPasswordModel, Body(...)],
            current_user: Annotated[UserModel, Depends(AuthService.get_current_user)]
    ) -> UserModel:
        """
        Update user's password.
        
        Args:
            data (UserEditPasswordModel): Password update information.
            current_user (Annotated[UserModel, Depends(AuthService.get_current_user)]): Current user.
        
        Returns:
            UserModel: Updated user model.
        """
        return UserService.update_user_password(current_user=current_user, data=data)
