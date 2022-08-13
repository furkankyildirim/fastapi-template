from typing import Optional
from pydantic.dataclasses import dataclass

from src.schemas.common import ExtraFieldsAllowedConfig


@dataclass(config=ExtraFieldsAllowedConfig)
class UserSchema:
    id: str
    name: str
    username: str
    email: str
    password: str
    profile_photo: Optional[str]


@dataclass(config=ExtraFieldsAllowedConfig)
class ProfilePhotoSchema:
    url: str
