from datetime import datetime

from src.database import UserDatabase
from src.models import UserModel, UserEditInfoModel, UserEditEmailModel, UserEditPasswordModel
from src.errors import BadRequestError, AuthorizationError
from src.utils.security import SecurityUtils
from src.utils.validation import ValidationUtils


class UserService:

    @staticmethod
    def get_user(current_user: UserModel, user_id: str) -> UserModel:
        """
        Get user:

        Args:
            current_user (UserModel): Current user.
            user_id (str): User ID.

        Returns:
            UserModel: User model.
        """
        if not current_user.is_admin and current_user.id != user_id:
            raise AuthorizationError(message="You are not allowed to view this user")

        user = UserDatabase.get_user(user_id=user_id)
        if not user:
            raise BadRequestError(message="User not found")
        return user

    @staticmethod
    def update_user_info(current_user: UserModel, data: UserEditInfoModel) -> UserModel:
        """
        Update user's first name and last name.
        
        Args:
            current_user (UserModel): Current user.
            data (UserEditInfoModel): Updated user information.
            
        Returns:
            UserModel: Updated user model.
        """
        if not data.name or not data.surname:
            raise BadRequestError(message="Name and surname cannot be empty.")

        current_user.name = data.name
        current_user.surname = data.surname

        return UserDatabase.update_user(user_id=current_user.id, user=current_user)

    @staticmethod
    async def update_user_email(current_user: UserModel, data: UserEditEmailModel) -> UserModel:
        """
        Update user's email address.
        
        Args:
            current_user (UserModel): Current user.
            data (UserEditEmailModel): Updated email information.
            
        Returns:
            UserModel: Updated user model.
        """
        from src.services.auth import AuthService  # Import here to avoid circular imports

        new_email = data.email

        # Validate new email with improved Gmail handling
        ValidationUtils.validate_email(email=new_email, skip_user_id=current_user.id)

        # Update user with new email
        current_user.email = new_email
        current_user.is_active = None

        updated_user = UserDatabase.update_user(user_id=current_user.id, user=current_user)

        # Send activation email to new address
        await AuthService.send_activation_email(user=updated_user)

        return updated_user

    @staticmethod
    def update_user_password(current_user: UserModel, data: UserEditPasswordModel) -> UserModel:
        """
        Update user's password.
        
        Args:
            current_user (UserModel): Current user.
            data (UserEditPasswordModel): Password change data.
            
        Returns:
            UserModel: Updated user model.
        """
        # Verify old password
        if not SecurityUtils.verify(hashed_password=current_user.password, plain_password=data.old_password):
            raise BadRequestError(message="Incorrect password.")

        # Validate new password strength
        ValidationUtils.validate_password(data.new_password)

        # Hash and update the new password
        current_user.password = SecurityUtils.bcrypt(text=data.new_password)
        current_user.updated_at = datetime.now()

        return UserDatabase.update_user(user_id=current_user.id, user=current_user)