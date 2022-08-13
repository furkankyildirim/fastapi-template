from typing import Any
from fastapi import APIRouter, Depends, UploadFile, File

from src.schemas.common import Response

from src.services import UserService, AuthenticationService
from src.utils import ImageResponse


class UserController:
    router = APIRouter()
    tags = ['Users']

    @staticmethod
    @router.get(
        "",
        response_model=Response[Any],
        summary="Get User by ID",
        response_model_by_alias=False,
        tags=tags,
    )
    def get_user(id: str) -> Response[Any]:
        """
        Get user from user id:

        - **user_id** (str): User ID.

        """
        return UserService.get_user(user_id=id)

    @staticmethod
    @router.get(
        "/current-user",
        response_model=Response[Any],
        summary="Get Current User",
        response_model_by_alias=False,
        tags=tags,
    )
    def get_current_user(current_user=Depends(AuthenticationService.get_current_user)) -> Response[Any]:
        """
        Get current user:

        - **current_user** (User): Current user.

        """
        return UserService.get_current_user(current_user=current_user)

    @staticmethod
    @router.get(
        "/profile-photo/{image}",
        response_model=Response[Any],
        summary="Get Profile Photo by Filename",
        response_model_by_alias=False,
        tags=tags
    )
    def get_profile_photo(image: str) -> ImageResponse:
        """
        Get profile photo by Filename:

        - **image** (User): Image Filename.

        """
        return UserService.get_profile_photo(image=image)

    @router.post(
        "/profile-photo",
        response_model=Response[Any],
        summary="Update Profile Photo",
        response_model_by_alias=False,
        tags=tags,
    )
    def update_profile_photo(current_user=Depends(AuthenticationService.get_current_user),
                             image: UploadFile = File(...)) -> Response[Any]:
        """
        Update profile photo:

        - **current_user** (User): Current user.

        """
        return UserService.update_profile_photo(current_user=current_user, image=image)

    @router.delete(
        "/profile-photo",
        response_model=Response[Any],
        summary="Delete Profile Photo",
        response_model_by_alias=False,
        tags=tags,
    )
    def delete_profile_photo(current_user=Depends(AuthenticationService.get_current_user)) -> Response[Any]:
        """
        Delete profile photo:

        - **current_user** (User): Current user.

        """
        return UserService.delete_profile_photo(current_user=current_user)
