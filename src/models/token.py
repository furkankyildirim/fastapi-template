from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field
from src.utils.security import SecurityUtils


class TokenType(str, Enum):
    """Enum for token types"""
    ACTIVATION = "activation"
    RESET_PASSWORD = "reset_password"


class TokenBaseModel(SQLModel):
    """Base model for token management"""
    token: str = Field(index=True, unique=True, max_length=255, description="The unique token string")
    token_type: TokenType = Field(index=True, description="Type of token (activation or reset_password)")
    expires_at: datetime = Field(index=True, description="When this token expires")
    is_used: bool = Field(default=False, description="Whether this token has been used")

    class Config:
        from_attributes = True
        populate_by_name = True


class TokenCreateModel(TokenBaseModel):
    """Model for creating new tokens"""
    pass


class TokenModel(TokenBaseModel, table=True):
    """Database model for tokens table"""
    __tablename__ = "tokens"

    id: str = Field(default_factory=SecurityUtils.id_generator, primary_key=True,
                    description="Unique identifier for the token")
    user_id: str = Field(index=True, foreign_key="users.id",
                         description="Foreign key to the user who owns this token")
    created_at: datetime = Field(default_factory=datetime.now, 
                                description="Timestamp when the token was created")

    class Config:
        from_attributes = True
        populate_by_name = True 