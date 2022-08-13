from sqlalchemy import Column, String

from src.database import PostgresqlConnection


class User(PostgresqlConnection.Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, index=True)
    profile_photo = Column(String)
