from typing import List
from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.exceptions import TransactionExceptions
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionQueryParams
)
from app.services.deps import get_transaction_service
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    params: TransactionQueryParams = Depends(),
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    transactions = transaction_service.get_user_transactions(
        user_id=current_user.id,
        params=params
    )
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    transaction = transaction_service.get_user_transaction_by_id(
        transaction_id=transaction_id,
        user_id=current_user.id
    )
    if not transaction:
        raise TransactionExceptions.transaction_not_found()
    return transaction


@router.post("/", response_model=TransactionResponse)
def create_new_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    created_transaction = transaction_service.create_user_transaction(
        transaction_data=transaction,
        user_id=current_user.id
    )
    if not created_transaction:
        raise TransactionExceptions.invalid_category()
    return created_transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_existing_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    updated_transaction = transaction_service.update_user_transaction(
        transaction_id=transaction_id,
        transaction_data=transaction,
        user_id=current_user.id
    )
    if not updated_transaction:
        existing = transaction_service.get_user_transaction_by_id(
            transaction_id=transaction_id,
            user_id=current_user.id
        )
        if not existing:
            raise TransactionExceptions.transaction_not_found()
        else:
            raise TransactionExceptions.invalid_category()
    return updated_transaction


@router.delete("/{transaction_id}")
def delete_existing_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    success = transaction_service.delete_user_transaction(
        transaction_id=transaction_id,
        user_id=current_user.id
    )
    if not success:
        raise TransactionExceptions.transaction_not_found()
    return {"message": "Transaction deleted successfully"}
