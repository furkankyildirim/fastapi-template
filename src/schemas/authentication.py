from pydantic.dataclasses import dataclass
from src.schemas.common import ExtraFieldsAllowedConfig


@dataclass(config=ExtraFieldsAllowedConfig)
class TokenSchema:
    token: str
    type: str = "bearer"


@dataclass(config=ExtraFieldsAllowedConfig)
class LoginSchema:
    email: str
    password: str


@dataclass(config=ExtraFieldsAllowedConfig)
class RegistrationSchema:
    name: str
    username: str
    email: str
    password: str
