from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_categories_for_user(db: Session, user_id: Optional[int] = None) -> List[Category]:
    if user_id is None:
        return db.query(Category).filter(Category.user_id.is_(None)).all()
    else:
        return db.query(Category).filter(
            or_(Category.user_id.is_(None), Category.user_id == user_id)
        ).all()


def get_category_by_id(db: Session, category_id: int, user_id: Optional[int] = None) -> Optional[Category]:
    if user_id is None:
        return db.query(Category).filter(
            and_(Category.id == category_id, Category.user_id.is_(None))
        ).first()
    else:
        return db.query(Category).filter(
            and_(
                Category.id == category_id,
                or_(Category.user_id.is_(None), Category.user_id == user_id)
            )
        ).first()


def create_category(db: Session, category_in: CategoryCreate, user_id: int) -> Category:
    db_category = Category(
        name=category_in.name,
        category_type=category_in.category_type,
        user_id=user_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category_update: CategoryUpdate, user_id: int) -> Optional[Category]:
    db_category = db.query(Category).filter(
        and_(Category.id == category_id, Category.user_id == user_id)
    ).first()

    if not db_category:
        return None

    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)

    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int, user_id: int) -> bool:
    db_category = db.query(Category).filter(
        and_(Category.id == category_id, Category.user_id == user_id)
    ).first()

    if not db_category:
        return False

    db.delete(db_category)
    db.commit()
    return True


def get_categories_by_type(db: Session, category_type: str, user_id: Optional[int] = None) -> List[Category]:
    base_query = db.query(Category).filter(
        Category.category_type == category_type)

    if user_id is None:
        return base_query.filter(Category.user_id.is_(None)).all()
    else:
        return base_query.filter(
            or_(Category.user_id.is_(None), Category.user_id == user_id)
        ).all()


def get_category_by_name(db: Session, name: str, user_id: Optional[int] = None) -> Optional[Category]:
    if user_id is None:
        return db.query(Category).filter(
            and_(Category.name == name, Category.user_id.is_(None))
        ).first()
    else:
        return db.query(Category).filter(
            and_(
                Category.name == name,
                or_(Category.user_id.is_(None), Category.user_id == user_id)
            )
        ).first()
