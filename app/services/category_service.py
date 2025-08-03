"""
Category service layer for handling business logic.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud.category import (
    get_categories_for_user,
    get_category_by_id,
    create_category,
    update_category,
    delete_category,
    get_categories_by_type
)
from app.models.category import Category, CategoryType
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """Service class for category-related business logic."""

    def __init__(self, db: Session):
        self.db = db

    def get_user_categories(
        self,
        user_id: Optional[int] = None,
        category_type: Optional[CategoryType] = None
    ) -> List[Category]:
        if category_type:
            return get_categories_by_type(
                db=self.db,
                category_type=category_type.value,
                user_id=user_id
            )
        else:
            return get_categories_for_user(
                db=self.db,
                user_id=user_id
            )

    def get_user_category_by_id(
        self,
        category_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Category]:
        return get_category_by_id(
            db=self.db,
            category_id=category_id,
            user_id=user_id
        )

    def create_user_category(
        self,
        category_data: CategoryCreate,
        user_id: int
    ) -> Optional[Category]:
        return create_category(
            db=self.db,
            category_in=category_data,
            user_id=user_id
        )

    def update_user_category(
        self,
        category_id: int,
        category_data: CategoryUpdate,
        user_id: int
    ) -> Optional[Category]:
        return update_category(
            db=self.db,
            category_id=category_id,
            category_update=category_data,
            user_id=user_id
        )

    def delete_user_category(
        self,
        category_id: int,
        user_id: int
    ) -> bool:
        return delete_category(
            db=self.db,
            category_id=category_id,
            user_id=user_id
        )
