from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.transaction import TransactionCreate, TransactionUpdate


def _validate_category_access(db: Session, category_id: int, user_id: int) -> Optional[Category]:
    return db.query(Category).filter(
        and_(
            Category.id == category_id,
            (Category.user_id == user_id) | (Category.user_id.is_(None))
        )
    ).first()


def _get_transaction_with_category(db: Session, transaction_id: int, user_id: int) -> Optional[Transaction]:
    return db.query(Transaction).options(
        joinedload(Transaction.category)
    ).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        )
    ).first()


def get_transaction_by_id(db: Session, transaction_id: int, user_id: int) -> Optional[Transaction]:
    return _get_transaction_with_category(db, transaction_id, user_id)


def get_transactions_for_user(
    db: Session,
    user_id: int,
    offset: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None
) -> List[Transaction]:

    query = db.query(Transaction).options(
        joinedload(Transaction.category)
    ).filter(Transaction.user_id == user_id)

    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    return query.offset(offset).limit(limit).all()


def create_transaction(db: Session, transaction: TransactionCreate, user_id: int) -> Optional[Transaction]:
    """Create a new transaction for the authenticated user."""
    
    category = _validate_category_access(db, transaction.category_id, user_id)
    if not category:
        return None

    db_transaction = Transaction(
        user_id=user_id,
        category_id=transaction.category_id,
        description=transaction.description,
        amount=transaction.amount,
        date=transaction.date
    )
    db.add(db_transaction)
    db.commit()

    return _get_transaction_with_category(db, db_transaction.id, user_id)


def update_transaction(
    db: Session,
    transaction_id: int,
    transaction_update: TransactionUpdate,
    user_id: int
) -> Optional[Transaction]:
    db_transaction = _get_transaction_with_category(
        db, transaction_id, user_id)
    if not db_transaction:
        return None

    update_data = transaction_update.model_dump(exclude_unset=True)

    if "category_id" in update_data:
        category = _validate_category_access(
            db, update_data["category_id"], user_id)
        if not category:
            return None

    for field, value in update_data.items():
        setattr(db_transaction, field, value)

    db.commit()

    if "category_id" in update_data:
        return _get_transaction_with_category(db, transaction_id, user_id)
    else:
        db.refresh(db_transaction)
        return db_transaction


def delete_transaction(db: Session, transaction_id: int, user_id: int) -> bool:
    db_transaction = _get_transaction_with_category(
        db, transaction_id, user_id)
    if not db_transaction:
        return False

    db.delete(db_transaction)
    db.commit()
    return True
