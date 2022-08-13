from src.errors import BAD_REQUEST_ERROR, NOT_FOUND_ERROR
from src.schemas.common import Response
from src.database import UserDatabase
from src.schemas import UserSchema, ProfilePhotoSchema
from src.utils import ImageUtils, ImageResponse


class UserService:
    @staticmethod
    def get_user(user_id: str) -> Response:
        """
        Get user:

        - user: UserSchema = User schema.

        """
        user = UserDatabase.get_user(user_id=user_id)
        if not user:
            raise NOT_FOUND_ERROR(message=f"User with the id {user_id} is not available")

        user.profile_photo = UserService.__set_photo_url(photo=user.profile_photo)
        return Response(isSuccess=True, data=user,
                        message="User with the id is returned successfully")

    @staticmethod
    def get_current_user(current_user) -> Response:
        """
        Get current user:

        - current_user: User = Current user.

        """
        current_user.profile_photo = UserService.__set_photo_url(photo=current_user.profile_photo)
        return Response(isSuccess=True, data=current_user,
                        message="Current user is returned successfully")

    @staticmethod
    def create_user(user: UserSchema) -> Response:
        """
        Create user:

        - user: UserSchema = User schema.

        """
        UserService._check_user_validations(email=user.email, username=user.username)
        user = UserDatabase.create_user(user=user)
        return Response(isSuccess=True, data=user, message="User is created successfully")

    @staticmethod
    def get_profile_photo(image: str) -> ImageResponse:
        """
        Get profile photo:

        - image: str =  Photo filename.

        """
        return ImageUtils.get_image(filename=image, subdir="profile")

    @staticmethod
    def update_profile_photo(current_user, image) -> Response:
        """
        Update profile photo:

        - current_user: User = Current user.
        - image: UploadFile = New image.

        """
        if current_user.profile_photo:
            filename: str = ImageUtils.get_filename_from_url(url=current_user.profile_photo)
            ImageUtils.delete_image(filename=filename, subdir="profile")

        filename: str = ImageUtils.upload_image(image=image, subdir="profile")
        prefix: str = ImageUtils.get_image_with_prefix(
            filename=filename, prefix="user/profile-photo")

        current_user = UserDatabase.update_profile_photo(current_user=current_user, image=prefix)

        if current_user.profile_photo != prefix:
            raise BAD_REQUEST_ERROR(message=f"Profile photo is not updated")

        profile_photo_url: str = ImageUtils.get_image_url_from_prefix(prefix=prefix)
        return Response(isSuccess=True, message="Profile photo is uploaded successfully",
                        data=ProfilePhotoSchema(url=profile_photo_url))

    @staticmethod
    def delete_profile_photo(current_user) -> Response:
        """
        Delete profile photo:

        - current_user: User = Current user.

        """
        if current_user.profile_photo:
            filename: str = ImageUtils.get_filename_from_url(url=current_user.profile_photo)
            ImageUtils.delete_image(filename=filename, subdir="profile")

        filename: str = ImageUtils.get_default_image()
        prefix: str = ImageUtils.get_image_with_prefix(
            filename=filename, prefix="user/profile-photo")

        current_user = UserDatabase.update_profile_photo(current_user=current_user, image=prefix)

        if current_user.profile_photo != prefix:
            raise BAD_REQUEST_ERROR(message=f"Profile photo is not updated")

        profile_photo_url: str = ImageUtils.get_image_url_from_prefix(prefix=prefix)
        return Response(isSuccess=True, message="Profile photo is deleted successfully",
                        data=ProfilePhotoSchema(url=profile_photo_url))

    @staticmethod
    def _set_user_schema(user) -> UserSchema:
        """
        Set profile photo url and user schema:

        - user: UserSchema = User schema.

        """
        user.profile_photo: str = UserService.__set_photo_url(photo=user.profile_photo)

        user: UserSchema = UserSchema(
            id=user.id,
            name=user.name,
            username=user.username,
            email=user.email,
            profile_photo=user.profile_photo,
        )

        return user

    @staticmethod
    def _validate_user_id(id: str) -> None:
        """
        Validate user id:

        - user_id: str = User id.

        """
        if not id:
            raise BAD_REQUEST_ERROR(message="User id is required")

        if not UserDatabase.get_user(user_id=id):
            raise NOT_FOUND_ERROR(message=f"User with the id {id} is not available")

    @staticmethod
    def _check_user_validations(email: str = None, username: str = None) -> None:
        """
        Checks if user validations are used before creating user:

        - email: str = Email.
        - username: str = Username.

        """
        if email and UserService.__check_email_is_used(email=email):
            raise BAD_REQUEST_ERROR(message=f"Email {email} is already used")
        if username and UserService.__check_username_is_used(username=username):
            raise BAD_REQUEST_ERROR(message=f"Username {username} is already used")

    @staticmethod
    def __check_email_is_used(email: str) -> bool:
        """
        Checks if email is used:

        - email: str = Email.

        """
        user = UserDatabase.get_user_by_email(email=email)
        return True if user else False

    @staticmethod
    def __check_username_is_used(username: str) -> bool:
        """
        Checks if username is used:

        - username: str = Username.

        """
        user = UserDatabase.get_user_by_username(username=username)
        return True if user else False

    @staticmethod
    def __set_photo_url(photo: str) -> str:
        """
        Set photo url:

        - photo: str = Photo filename.

        """
        return ImageUtils.get_image_url_from_prefix(prefix=photo)
