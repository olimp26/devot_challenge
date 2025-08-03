"""
Auth service layer for handling authentication business logic.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.crud.user import authenticate_user, create_user, get_user_by_email
from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:
    """Service class for authentication-related business logic."""

    def __init__(self, db: Session):
        self.db = db

    def authenticate_user_credentials(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        return authenticate_user(
            db=self.db,
            email=email,
            password=password
        )

    def get_user_by_email(
        self,
        email: str
    ) -> Optional[User]:
        return get_user_by_email(
            db=self.db,
            email=email
        )

    def create_new_user(
        self,
        user_data: UserCreate
    ) -> User:
        return create_user(
            db=self.db,
            user_in=user_data
        )
