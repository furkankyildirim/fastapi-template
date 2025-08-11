from pydantic import BaseModel


class TokenRequestModel(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True
        populate_by_name = True


class RefreshTokenModel(BaseModel):
    refresh: str

    class Config:
        from_attributes = True
        populate_by_name = True


class TokenResponseModel(RefreshTokenModel):
    access: str


class LoginModel(TokenRequestModel):
    remember_me: bool = False


class APIKeyInfoModel(BaseModel):
    user_id: str
    company_id: str | None
    scope: str
    role: str
    expires_at: float
    created_at: float

    class Config:
        from_attributes = True
        populate_by_name = True
