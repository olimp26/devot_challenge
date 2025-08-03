from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.category import CategoryType


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100,
                      description="Category name")
    category_type: CategoryType = Field(...,
                                        description="Category type: income or expense")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Category name")
    category_type: Optional[CategoryType] = Field(
        None, description="Category type: income or expense")


class CategoryResponse(CategoryBase):
    id: int
    user_id: Optional[int] = None
    last_changed: datetime

    model_config = ConfigDict(from_attributes=True)
