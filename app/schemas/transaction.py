from datetime import date as date_type, datetime
from decimal import Decimal
from typing import Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.models.category import CategoryType


def validate_transaction_amount(v: Optional[Decimal]) -> Optional[Decimal]:
    if v is not None:
        if v < 0:
            raise ValueError('Amount must be greater than or equal to 0')

        if v.as_tuple().exponent < -2:
            raise ValueError('Amount can have at most 2 decimal places')
    return v


class TransactionBase(BaseModel):
    category_id: int = Field(...,
                             description="Category ID")
    description: str = Field(..., min_length=1, max_length=500,
                             description="Transaction description")
    amount: Decimal = Field(...,
                            description="Transaction amount (must be >= 0)")
    date: Union[date_type, None] = Field(
        default=None, description="Transaction date (defaults to current date)")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        return validate_transaction_amount(v)


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    category_id: Optional[int] = Field(
        default=None, description="Category ID")
    description: Optional[str] = Field(
        default=None, min_length=1, max_length=500, description="Transaction description")
    amount: Optional[Decimal] = Field(
        default=None, ge=0, description="Transaction amount (must be >= 0)")
    date: Union[date_type, None] = Field(
        default=None, description="Transaction date")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        return validate_transaction_amount(v)


class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    last_changed: datetime
    category_name: str
    category_type: str

    model_config = ConfigDict(from_attributes=True)


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class SortField(str, Enum):
    DATE = "date"
    AMOUNT = "amount"
    DESCRIPTION = "description"
    LAST_CHANGED = "last_changed"


class TransactionQueryParams(BaseModel):
    """Query parameters for filtering and sorting transactions."""
    offset: int = Field(
        default=0, ge=0, description="Number of transactions to skip")
    limit: int = Field(default=100, ge=1, le=1000,
                       description="Maximum number of transactions to return")
    category_id: Optional[int] = Field(
        default=None, description="Filter by category ID")
    min_amount: Optional[Decimal] = Field(
        default=None, ge=0, description="Minimum transaction amount")
    max_amount: Optional[Decimal] = Field(
        default=None, ge=0, description="Maximum transaction amount")
    from_date: Optional[date_type] = Field(
        default=None, description="Start date for filtering (YYYY-MM-DD)")
    to_date: Optional[date_type] = Field(
        default=None, description="End date for filtering (YYYY-MM-DD)")
    category_type: Optional[CategoryType] = Field(
        default=None, description="Filter by transaction type (income/expense)")
    description_query: Optional[str] = Field(default=None, min_length=1,
                                             max_length=100, description="Search keyword in description")
    sort_by: SortField = Field(
        default=SortField.DATE, description="Field to sort by")
    order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")

    model_config = ConfigDict(
        use_enum_values=True
    )
