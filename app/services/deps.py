from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.services.transaction_service import TransactionService
from app.services.category_service import CategoryService
from app.services.auth_service import AuthService
from app.services.summary_service import SummaryService


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


def get_transaction_service(
    db: Session = Depends(get_db),
    category_service: CategoryService = Depends(get_category_service)
) -> TransactionService:
    return TransactionService(db, category_service)


def get_auth_service(
    db: Session = Depends(get_db),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> AuthService:
    return AuthService(db, transaction_service)


def get_summary_service(
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> SummaryService:
    return SummaryService(transaction_service)
