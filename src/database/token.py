from datetime import datetime
from typing import Optional
from sqlmodel import select

from src.database.connections import postgres_session as session
from src.models.token import TokenModel, TokenCreateModel, TokenType
from src.errors import BadRequestError


class TokenDatabase:
    @staticmethod
    def get_token(token_id: str) -> Optional[TokenModel]:
        """
        Get token by ID:

        Args:
            token_id (str): Token ID.

        Returns:
            TokenModel: Token model.
        """
        return session.get(TokenModel, token_id)

    @staticmethod
    def get_token_by_value(token: str) -> Optional[TokenModel]:
        """
        Get token by token value:

        Args:
            token (str): Token value.

        Returns:
            TokenModel: Token model.
        """
        return session.exec(select(TokenModel).where(
            TokenModel.token == token,
            TokenModel.is_used == False
        )).first()

    @staticmethod
    def get_valid_token(token: str, token_type: TokenType) -> Optional[TokenModel]:
        """
        Get valid token by token value and type:

        Args:
            token (str): Token value.
            token_type (TokenType): Token type.

        Returns:
            TokenModel: Token model if valid and not expired.
        """
        db_token = session.exec(select(TokenModel).where(
            TokenModel.token == token,
            TokenModel.token_type == token_type,
            TokenModel.is_used == False
        )).first()
        
        # Check if token exists and hasn't expired
        if db_token and db_token.expires_at > datetime.now():
            return db_token
        
        return None

    @staticmethod
    def create_token(user_id: str, token_data: TokenCreateModel) -> TokenModel:
        """
        Create new token:

        Args:
            user_id (str): User ID.
            token_data (TokenCreateModel): Token create model.

        Returns:
            TokenModel: New token model.
        """
        db_token = TokenModel(
            **token_data.model_dump(),
            user_id=user_id
        )

        session.add(db_token)
        session.commit()
        session.refresh(db_token)
        return db_token

    @staticmethod
    def mark_token_as_used(token: str) -> bool:
        """
        Mark token as used:

        Args:
            token (str): Token value.

        Returns:
            bool: True if successful.
        """
        db_token = session.exec(select(TokenModel).where(
            TokenModel.token == token,
            TokenModel.is_used == False
        )).first()
        
        if db_token:
            db_token.is_used = True
            session.commit()
            return True
        
        return False

    @staticmethod
    def delete_token(token: str) -> bool:
        """
        Delete token:

        Args:
            token (str): Token value.

        Returns:
            bool: True if successful.
        """
        db_token = session.exec(select(TokenModel).where(TokenModel.token == token)).first()
        
        if db_token:
            session.delete(db_token)
            session.commit()
            return True
        
        return False

    @staticmethod
    def cleanup_expired_tokens() -> int:
        """
        Clean up expired tokens:

        Returns:
            int: Number of tokens deleted.
        """
        expired_tokens = session.exec(select(TokenModel).where(
            TokenModel.expires_at < datetime.now()
        )).all()
        
        count = len(expired_tokens)
        
        for token in expired_tokens:
            session.delete(token)
        
        session.commit()
        return count

    @staticmethod
    def get_user_tokens(user_id: str, token_type: Optional[TokenType] = None) -> list[TokenModel]:
        """
        Get tokens for a user:

        Args:
            user_id (str): User ID.
            token_type (TokenType, optional): Filter by token type.

        Returns:
            list[TokenModel]: List of token models.
        """
        query = select(TokenModel).where(TokenModel.user_id == user_id)
        
        if token_type:
            query = query.where(TokenModel.token_type == token_type)
        
        return session.exec(query).all() 