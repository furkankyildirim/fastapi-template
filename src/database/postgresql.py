from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.configs import AppConfig


class PostgresqlConnection:
    """
    PostgreSQL connector
    """

    Base = declarative_base()

    def __init__(self) -> None:
        """
        Initialize PostgreSQL connector
        """
        self.establish_connection()

    def __call__(self) -> Generator:
        """
        Create a new session
        """
        try:
            db = self.session()
            yield db
        finally:
            db.close()

    def establish_connection(self) -> None:
        """
        Establishes connection to PostgreSQL database
        """
        self.engine = create_engine(AppConfig.DATABASE_URL, pool_pre_ping=True)
        self.session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
