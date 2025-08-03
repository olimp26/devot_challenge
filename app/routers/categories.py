from typing import List, Optional
from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_user, get_current_user_optional
from app.core.exceptions import CategoryExceptions
from app.models.user import User
from app.models.category import CategoryType
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.deps import get_category_service
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryResponse], summary="Get all accessible categories")
def get_categories(
    category_type: Optional[CategoryType] = Query(
        None, description="Filter by category type"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    category_service: CategoryService = Depends(get_category_service)
):
    user_id = current_user.id if current_user else None
    categories = category_service.get_user_categories(
        user_id=user_id,
        category_type=category_type
    )
    return categories


@router.get("/{category_id}", response_model=CategoryResponse, summary="Get category by ID")
def get_category(
    category_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    category_service: CategoryService = Depends(get_category_service)
):
    user_id = current_user.id if current_user else None
    category = category_service.get_user_category_by_id(
        category_id=category_id,
        user_id=user_id
    )

    if not category:
        raise CategoryExceptions.category_not_found()

    return category


@router.post("/", response_model=CategoryResponse, summary="Create a new category")
def create_category_endpoint(
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service)
):
    category = category_service.create_user_category(
        category_data=category_in,
        user_id=current_user.id
    )
    return category


@router.put("/{category_id}", response_model=CategoryResponse, summary="Update a category")
def update_category_endpoint(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service)
):
    category = category_service.update_user_category(
        category_id=category_id,
        category_data=category_update,
        user_id=current_user.id
    )

    if not category:
        raise CategoryExceptions.category_update_denied()

    return category


@router.delete("/{category_id}", summary="Delete a category")
def delete_category_endpoint(
    category_id: int,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service)
):
    success = category_service.delete_user_category(
        category_id=category_id,
        user_id=current_user.id
    )

    if not success:
        raise CategoryExceptions.category_delete_denied()

    return {"message": "Category deleted successfully"}
