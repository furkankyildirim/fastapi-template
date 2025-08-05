from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class BaseConfig(BaseSettings):
    # General application settings
    DEBUG: bool = Field(default=False)
    NAME: str = Field(default="FastAPI Template")
    DESCRIPTION: str = Field(default="A simple async MVC API")
    VERSION: str = Field(default="0.0.1")
    TEST_URL: str = Field(default="http://localhost:8002")
    PROD_URL: str = Field(default="https://api.flio.ai")

    URL: str = None

    # Security settings
    SECRET_KEY: str = Field(default="secret")
    HASHING_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    # PostgreSQL settings
    POSTGRES_USER: str = Field(...)
    POSTGRES_PASSWORD: str = Field(...)
    POSTGRES_SERVER: str = Field(default="localhost")

    POSTGRES_DEV_USER: str = Field(default="postgres")
    POSTGRES_DEV_PASSWORD: str = Field(default="123456")
    POSTGRES_DEV_SERVER: str = Field(default="localhost")

    POSTGRES_PORT: str = Field(default="5432")  # default PostgreSQL port
    POSTGRES_DB: str = Field(...)
    DATABASE_URL: str = None

    # Redis settings
    # REDIS_URL: str = Field(default="redis://localhost:6379")
    # REDIS_PREFIX: str = Field(default="fastapi")
    # REDIS_TTL: int = Field(default=60 * 60 * 24 * 30)  # 30 days

    # Boto3 settings
    AWS_ACCESS_KEY_ID: str = Field(...)
    AWS_SECRET_ACCESS_KEY: str = Field(...)
    AWS_REGION: str = Field(...)
    AWS_SES_SENDER: str = Field(...)

    @field_validator("URL", mode="before")
    def assemble_url(cls, v, values: ValidationInfo):
        """Assemble the application URL."""
        if v:
            return v
        test_url = values.data.get('TEST_URL')
        prod_url = values.data.get('PROD_URL')
        debug = values.data.get('DEBUG')

        return test_url if debug else prod_url

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v, values: ValidationInfo):
        """Assemble the PostgreSQL connection URL."""
        if v:
            return v

        postgres_user = values.data.get('POSTGRES_USER' if not values.data.get('DEBUG') else 'POSTGRES_DEV_USER')
        postgres_password = values.data.get(
            'POSTGRES_PASSWORD' if not values.data.get('DEBUG') else 'POSTGRES_DEV_PASSWORD')
        postgres_server = values.data.get('POSTGRES_SERVER' if not values.data.get('DEBUG') else 'POSTGRES_DEV_SERVER')
        postgres_port = values.data.get('POSTGRES_PORT')
        postgres_db = values.data.get('POSTGRES_DB')

        return f"postgresql://{postgres_user}:{postgres_password}@{postgres_server}:{postgres_port}/{postgres_db}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Initialize configuration
AppConfig = BaseConfig()
