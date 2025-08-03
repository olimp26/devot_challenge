from typing import List, Optional
from sqlalchemy.orm import Session

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


class TransactionService:
    """Service class for transaction-related business logic."""

    def __init__(self, db: Session):
        self.db = db

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
