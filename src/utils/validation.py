import re
from src.errors import BadRequestError, ValidationError
from src.database import UserDatabase


class ValidationUtils:
    @staticmethod
    def validate_email(email: str, skip_user_id: str = None) -> bool:
        """
        Validate email format and check if it already exists.
        For Gmail addresses, it checks equivalent emails (ignoring dots in local part).

        Args:
            email (str): Email to validate
            skip_user_id (str, optional): User ID to skip during uniqueness check (for updates)

        Returns:
            bool: True if email is valid and unique

        Raises:
            ValidationError: If email format is invalid
            BadRequestError: If email already exists
        """
        # Validate email format
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            raise ValidationError(message="Invalid email format")

        # For Gmail addresses, check equivalent emails
        if email.lower().endswith("@gmail.com"):
            # Remove dots from local part for comparison
            local_part = email.lower().split("@")[0].replace(".", "")

            # Get all users with Gmail accounts
            gmail_users = UserDatabase.filter_users_by_email_domain("gmail.com")

            # Check if normalized version of email already exists
            for user in gmail_users:
                if skip_user_id and user.id == skip_user_id:
                    continue  # Skip current user during updates

                user_local_part = user.email.lower().split("@")[0].replace(".", "")
                if user_local_part == local_part:
                    raise BadRequestError(message="Email already exists (Gmail equivalent)")
        else:
            # For non-Gmail addresses, simply check if email exists
            existing_user = UserDatabase.get_user_by_email(email=email)
            if existing_user and (not skip_user_id or existing_user.id != skip_user_id):
                raise BadRequestError(message="Email already exists")

        return True

    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Validate password strength.

        Args:
            password (str): Password to validate

        Returns:
            bool: True if password meets strength requirements

        Raises:
            BadRequestError: If password doesn't meet the requirements
        """
        # Check length
        if len(password) < 8:
            raise BadRequestError(message="Password must be at least 8 characters long")

        # Check complexity using regex
        # if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$", password):
        #     raise BadRequestError(
        #         message="Password must include at least one lowercase letter, one uppercase letter, one number, and one special character"
        #     )

        return True
