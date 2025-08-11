from pydantic import BaseModel, Field as PydanticField
from sqlmodel import SQLModel, Field

from datetime import datetime, date

from src.constants import UserConstant
from src.utils.security import SecurityUtils


class UserBaseModel(SQLModel):
    __tablename__ = "users"

    name: str = Field(index=True)
    surname: str = Field(index=True)

    email: str = Field(index=True, unique=True,
                       regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                       description="Email must be valid and follow standard email format."
                       )

    class Config:
        from_attributes = True
        populate_by_name = True


class UserCreateModel(UserBaseModel):
    password: str = Field(exclude=True, default=None)

    class Config:
        from_attributes = True
        populate_by_name = True


class UserSubscriptionModel(SQLModel):
    subscription: UserConstant.Subscription = Field(default=UserConstant.Subscription.FREE)
    credit: float = Field(default=0.0)
    exp_date: date = Field(default_factory=date.today)


class UserModel(UserCreateModel, UserSubscriptionModel, table=True):
    id: str = Field(default_factory=SecurityUtils.id_generator, primary_key=True, alias="id")
    is_active: bool | None = Field(default=None, alias="isActive")
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    role: UserConstant.Role = Field(default=UserConstant.Role.USER)

    @property
    def is_user(self):
        return self.role == UserConstant.Role.USER

    @property
    def is_admin(self):
        return self.role == UserConstant.Role.ADMIN

    @property
    def is_activated(self):
        return self.is_active or self.is_active is None


class UserEditInfoModel(BaseModel):
    """
    Model for updating user's first and last name.
    """
    name: str = PydanticField(..., min_length=1, description="User's first name")
    surname: str = PydanticField(..., min_length=1, description="User's last name")


class UserEditEmailModel(BaseModel):
    """
    Model for updating user's email address.
    """
    email: str = PydanticField(...,
                               description="New email address, must be valid and follow standard email format")


class UserEditPasswordModel(BaseModel):
    """
    Model for updating user's password.
    """
    old_password: str = PydanticField(..., description="Current password")
    new_password: str = PydanticField(...,
                                      min_length=8,
                                      description="New password, must be at least 8 characters long.")

