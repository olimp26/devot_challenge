from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import UserExceptions
from app.core.security import get_current_user_email, verify_token
from app.crud.user import get_user_by_email
from app.db.session import get_db
from app.models.user import User

optional_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
) -> User:
    user = get_user_by_email(db, email=current_user_email)
    if user is None:
        raise UserExceptions.user_not_found()
    return user


def get_current_user_optional(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(optional_bearer)
) -> Optional[User]:
    if token is None:
        return None

    try:
        if hasattr(token, 'credentials'):
            token_str = token.credentials
        else:
            token_str = str(token)

        user_email = verify_token(token_str)
        user = get_user_by_email(db, email=user_email)
        return user
    except HTTPException:
        # Invalid token, but no error raised for optional auth
        return None
