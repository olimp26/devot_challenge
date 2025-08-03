from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.exceptions import UserExceptions
from app.core.security import get_current_user_email
from app.crud.user import get_user_by_email
from app.db.session import get_db
from app.models.user import User


def get_current_user(
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
) -> User:
    user = get_user_by_email(db, email=current_user_email)
    if user is None:
        raise UserExceptions.user_not_found()
    return user
