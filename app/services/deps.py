from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.services.transaction_service import TransactionService
from app.services.category_service import CategoryService
from app.services.auth_service import AuthService


def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    return TransactionService(db)


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)
