from dotenv import load_dotenv
from os import getcwd, environ as env

load_dotenv()

DEBUG = env.get('DEBUG', 'False').lower() in ('true', '1', 't')
URL = env.get('DEVELOPMENT_URL', 'http://127.0.0.1:8000') if DEBUG else env.get('PRODUCTION_URL', None)


class AppConfig:
    DEBUG: bool = DEBUG
    TESTING: bool = env.get('TESTING', 'False').lower() in ('true', '1', 't')

    NAME: str = env.get('NAME', 'FastAPI Template')
    DESCRIPTION: str = env.get('DESCRIPTION', 'FastAPI Template using Docker, PostgreSQL and SQLAlchemy')
    VERSION: str = env.get('VERSION', 'api/v1')

    URL = URL
    API_URL: str = URL + '/api'
    SECRET_KEY: str = env.get('SECRET_KEY', 'secret')
    HASHING_ALGORITHM: str = env.get('HASHING_ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(env.get('ACCESS_TOKEN_EXPIRE_MINUTES', 30))

    MEDIA_FOLDER: str = getcwd() + env.get('MEDIA_FOLDER', '/media')
    STATIC_FOLDER: str = getcwd() + env.get('STATIC_FOLDER', '/static')
    NO_PHOTO_FILE: str = env.get('NO_PHOTO_FILE')

    POSTGRES_USER: str = env.get("POSTGRES_USER")
    POSTGRES_PASSWORD = env.get("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = env.get("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = env.get("POSTGRES_PORT", 5432)  # default postgres port is 5432
    POSTGRES_DB: str = env.get("POSTGRES_DB", "postgres")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
