from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.exceptions import TransactionExceptions
from app.crud.transaction import (
    get_transactions_for_user,
    get_transaction_by_id,
    create_transaction,
    update_transaction,
    delete_transaction
)
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    skip: int = Query(0, ge=0, description="Number of transactions to skip"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Maximum number of transactions to return"),
    category_id: Optional[int] = Query(
        None, description="Filter by category ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transactions = get_transactions_for_user(
        db=db,
        user_id=current_user.id,
        offset=skip,
        limit=limit,
        category_id=category_id
    )
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = get_transaction_by_id(
        db=db, transaction_id=transaction_id, user_id=current_user.id)
    if not transaction:
        raise TransactionExceptions.transaction_not_found()
    return transaction


@router.post("/", response_model=TransactionResponse)
def create_new_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_transaction = create_transaction(
        db=db, transaction=transaction, user_id=current_user.id)
    if not db_transaction:
        raise TransactionExceptions.invalid_category()
    return db_transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_existing_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_transaction = update_transaction(
        db=db,
        transaction_id=transaction_id,
        transaction_update=transaction,
        user_id=current_user.id
    )
    if not db_transaction:
        existing = get_transaction_by_id(
            db=db, transaction_id=transaction_id, user_id=current_user.id)
        if not existing:
            raise TransactionExceptions.transaction_not_found()
        else:
            raise TransactionExceptions.invalid_category()
    return db_transaction


@router.delete("/{transaction_id}")
def delete_existing_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = delete_transaction(
        db=db, transaction_id=transaction_id, user_id=current_user.id)
    if not success:
        raise TransactionExceptions.transaction_not_found()
    return {"message": "Transaction deleted successfully"}
