from typing import Union
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from src.database import PostgresqlConnection
from src.models import User
from src.schemas import UserSchema


class UserDatabase:
    _postgre_connection = PostgresqlConnection()

    @staticmethod
    def get_user(user_id: str) -> Union[User, None]:
        """
        Get user:
            
        - user_id: int = User ID.
            
        """

        db: Session = next(UserDatabase._postgre_connection())
        user: User = db.query(User).filter(User.id == user_id).first()
        return user

    @staticmethod
    def get_user_by_email(email: str) -> Union[UserSchema, None]:
        """
        Get user:
            
        - email: str = User email.
            
        """

        db: Session = next(UserDatabase._postgre_connection())
        user: User = db.query(User).filter(User.email == email).first()
        return user

    @staticmethod
    def get_user_by_username(username: str) -> Union[UserSchema, None]:
        """
        Get user:
            
        - username: str = User username.
            
        """

        db: Session = next(UserDatabase._postgre_connection())
        user: User = db.query(User).filter(User.username == username).first()
        return user

    @staticmethod
    def update_profile_photo(current_user: UserSchema, image: str) -> Union[UserSchema, None]:
        """
        Update profile photo:

        - current_user: UserSchema = Current user.
        - image: str = Photo filename.
            
        """

        db: Session = next(UserDatabase._postgre_connection())
        user: User = db.query(User).filter(User.id == current_user.id).first()
        user.profile_photo = image
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def create_user(user: UserSchema):
        """
        Create user:
            
        - user: UserSchema = User schema.
            
        """

        db: Session = next(UserDatabase._postgre_connection())
        user_model = User(**jsonable_encoder(user))
        db.add(user_model)
        db.commit()
        db.refresh(user_model)
        return user
