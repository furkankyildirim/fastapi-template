from datetime import datetime, date, timedelta
from sqlmodel import select

from src.database.connections import postgres_session as session
from src.models import UserModel, UserCreateModel


class UserDatabase:
    @staticmethod
    def get_user(user_id: str) -> UserModel:
        """
        Get user by ID:

        Args:
            user_id (str): User ID.

        Returns:
            UserModel: User model.
        """
        return session.get(UserModel, user_id)

    @staticmethod
    def get_user_by_email(email: str) -> UserModel:
        """
        Get user by email:

        Args:
            email (str): Email.

        Returns:
            UserAuthModel: User authentication model.
        """
        db_user = session.exec(select(UserModel).where(UserModel.email == email)).first()
        return db_user

    @staticmethod
    def get_users(company_id: str, limit: int, offset: int) -> list[UserModel]:
        """
        Get users:

        Args:
            company_id (str): Company ID.
            limit (int): Limit.
            offset (int): Offset.

        Returns:
            list[UserModel]: List of user models.
        """
        return session.exec(select(UserModel).where(UserModel.company_id == company_id).offset(offset).limit(limit)).all()

    @staticmethod
    def create_user(user: UserCreateModel) -> UserModel:
        """
        Create user:

        Args:
            user (UserCreateModel): User create model.

        Returns:
            UserModel: User model.
        """

        db_user = UserModel.model_validate(user)
    
        db_user.credit = 10.0
        db_user.exp_date = date.today() + timedelta(days=7)

        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(user_id: str, user: UserModel) -> UserModel:
        """
        Update user:

        Args:
            user_id (str): User ID.
            user (UserCreateModel): User create model.

        Returns:
            UserModel: User model.
        """
        user.updated_at = datetime.now()

        db_user = UserDatabase.get_user(user_id)
        # SQLModel doesn't support direct update with session.exec, so we need to use a different approach
        db_user = UserDatabase.get_user(user_id)
        if db_user:
            for key, value in user.model_dump().items():
                setattr(db_user, key, value)
            session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

    @staticmethod
    def filter_users_by_email_domain(domain: str) -> list[UserModel]:
        """
        Filter users by email domain:

        Args:
            domain (str): Email domain (e.g., 'gmail.com').

        Returns:
            list[UserModel]: List of user models with the specified email domain.
        """
        return session.exec(select(UserModel).where(UserModel.email.endswith(f"@{domain}"))).all()
