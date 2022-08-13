from datetime import datetime, timedelta
import uuid
from fastapi.security import OAuth2PasswordBearer
from typing import Dict
from passlib.context import CryptContext
from jose import jwt
import string
import random

from src.configs.app import AppConfig

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash():
    reusable_oauth2 = OAuth2PasswordBearer(
        tokenUrl=f"/api/authentication/login-form", auto_error=False
    )

    def bcrypt(password: str) -> str:
        return pwd_cxt.hash(password)

    def verify(hashed_password,plain_password) -> bool:
        return pwd_cxt.verify(plain_password,hashed_password)

    def id_generator() -> str:
        return str(uuid.uuid1())

    def code_generator(size=6, chars=string.digits) -> str:
        return ''.join(random.choice(chars) for _ in range(size))

    def generate_token(text: str) -> str:
        payload = {
            "sub": text,
            "exp": datetime.utcnow() + timedelta(minutes=AppConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
        }

        token : str = jwt.encode(payload, AppConfig.SECRET_KEY, algorithm=AppConfig.HASHING_ALGORITHM)
        return token

    def decode_token(token: str) -> str:
        payload : Dict = jwt.decode(token, AppConfig.SECRET_KEY, algorithms=[AppConfig.HASHING_ALGORITHM])
        text: str = payload["sub"]
        return text

