from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date

from app.crud.transaction import (
    get_transactions_for_user,
    get_transaction_by_id,
    create_transaction,
    update_transaction,
    delete_transaction
)
from app.models.transaction import Transaction
from app.models.category import CategoryType
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionQueryParams
)
from app.core.config import get_settings


class TransactionService:
    """Service class for transaction-related business logic."""

    def __init__(self, db: Session, category_service=None):
        self.db = db
        self.category_service = category_service

    def get_user_transactions(
        self,
        user_id: int,
        params: TransactionQueryParams
    ) -> List[Transaction]:
        return get_transactions_for_user(
            db=self.db,
            user_id=user_id,
            offset=params.offset,
            limit=params.limit,
            category_id=params.category_id,
            min_amount=params.min_amount,
            max_amount=params.max_amount,
            from_date=params.from_date,
            to_date=params.to_date,
            category_type=params.category_type,
            description_query=params.description_query,
            sort_by=params.sort_by,
            order=params.order
        )

    def get_user_transaction_by_id(
        self,
        transaction_id: int,
        user_id: int
    ) -> Optional[Transaction]:
        return get_transaction_by_id(
            db=self.db,
            transaction_id=transaction_id,
            user_id=user_id
        )

    def create_user_transaction(
        self,
        transaction_data: TransactionCreate,
        user_id: int
    ) -> Optional[Transaction]:
        return create_transaction(
            db=self.db,
            transaction=transaction_data,
            user_id=user_id
        )

    def update_user_transaction(
        self,
        transaction_id: int,
        transaction_data: TransactionUpdate,
        user_id: int
    ) -> Optional[Transaction]:
        return update_transaction(
            db=self.db,
            transaction_id=transaction_id,
            transaction_update=transaction_data,
            user_id=user_id
        )

    def delete_user_transaction(
        self,
        transaction_id: int,
        user_id: int
    ) -> bool:
        return delete_transaction(
            db=self.db,
            transaction_id=transaction_id,
            user_id=user_id
        )

    def create_initial_transaction(self, user_id: int) -> Optional[Transaction]:
        settings = get_settings()

        if not self.category_service:
            return None

        other_income_category = self.category_service.get_category_by_name(
            name="Other Income",
            user_id=None
        )

        if other_income_category:
            initial_transaction = TransactionCreate(
                category_id=other_income_category.id,
                description="Predefined amount of money on account",
                amount=settings.initial_transaction_amount,
                date=date.today()
            )

            return create_transaction(
                db=self.db,
                transaction=initial_transaction,
                user_id=user_id
            )

        return None
