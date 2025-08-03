from datetime import date as date_type, datetime
from decimal import Decimal
from typing import Optional, Union

from pydantic import BaseModel, Field, ConfigDict, field_validator


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
