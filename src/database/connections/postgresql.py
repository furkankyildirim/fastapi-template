from sqlmodel import SQLModel, Field, create_engine, Session
from fastapi import Depends

from src.configs import AppConfig
from src.utils.common import Singleton


class PostgresqlConnection(metaclass=Singleton):
    """
    PostgreSQL connector using Singleton pattern with SQLModel.
    """

    def __init__(self) -> None:
        """
        Initialize PostgreSQL connector and create the database engine.
        """
        self.engine = create_engine(
            AppConfig.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        
        # Create a single global session
        self.session = Session(
            self.engine,
            autocommit=False,
            autoflush=False
        )

    def get_session(self) -> Session:
        """
        Get the global session.
        """
        return self.session

    def create_db_and_tables(self):
        """
        Create all tables in the database.
        """
        SQLModel.metadata.create_all(self.engine)


# Singleton instance of PostgresqlConnection
postgres_connection = PostgresqlConnection()

# Get the global session that will be reused
postgres_session = postgres_connection.get_session()