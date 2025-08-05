from datetime import datetime, timedelta, timezone
import uuid
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from typing import Dict
from passlib.context import CryptContext
from jose import jwt
import hashlib

from src.configs.app import AppConfig

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityUtils:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

    @staticmethod
    def bcrypt(text: str) -> str:
        return pwd_cxt.hash(text)

    @staticmethod
    def verify(hashed_password, plain_password) -> bool:
        return pwd_cxt.verify(plain_password, hashed_password)

    @staticmethod
    def id_generator() -> str:
        return uuid.uuid1().hex

    @staticmethod
    def sha256(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def generate_token(text: str) -> Dict:
        access_token = {
            "sub": text,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=AppConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
        }

        refresh_token = {
            "sub": text,
            "exp": datetime.now(timezone.utc) + timedelta(days=1000)
        }

        payload = {
            "access": jwt.encode(access_token, AppConfig.SECRET_KEY, algorithm=AppConfig.HASHING_ALGORITHM),
            "refresh": jwt.encode(refresh_token, AppConfig.SECRET_KEY, algorithm=AppConfig.HASHING_ALGORITHM)
        }

        return payload

    @staticmethod
    def decode_token(token: str) -> str:
        payload: Dict = jwt.decode(token, AppConfig.SECRET_KEY, algorithms=[AppConfig.HASHING_ALGORITHM])
        text: str = payload["sub"]
        return text
