from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_current_user_optional
from app.core.exceptions import CategoryExceptions
from app.crud.category import (
    get_categories_for_user,
    get_category_by_id,
    create_category,
    update_category,
    delete_category,
    get_categories_by_type
)
from app.db.session import get_db
from app.models.user import User
from app.models.category import CategoryType
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryResponse], summary="Get all accessible categories")
def get_categories(
    category_type: Optional[CategoryType] = Query(
        None, description="Filter by category type"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None

    if category_type:
        categories = get_categories_by_type(db, category_type.value, user_id)
    else:
        categories = get_categories_for_user(db, user_id)

    return categories


@router.get("/{category_id}", response_model=CategoryResponse, summary="Get category by ID")
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    category = get_category_by_id(db, category_id, user_id)

    if not category:
        raise CategoryExceptions.category_not_found()

    return category


@router.post("/", response_model=CategoryResponse, summary="Create a new category")
def create_category_endpoint(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = create_category(db, category_in, current_user.id)
    return category


@router.put("/{category_id}", response_model=CategoryResponse, summary="Update a category")
def update_category_endpoint(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = update_category(
        db, category_id, category_update, current_user.id)

    if not category:
        raise CategoryExceptions.category_update_denied()

    return category


@router.delete("/{category_id}", summary="Delete a category")
def delete_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = delete_category(db, category_id, current_user.id)

    if not success:
        raise CategoryExceptions.category_delete_denied()

    return {"message": "Category deleted successfully"}
