from decimal import Decimal
from typing import List, Optional
from datetime import date as date_type

from pydantic import BaseModel, Field


class CategoryBreakdownItem(BaseModel):
    category: str = Field(..., description="Category name")
    total: Decimal = Field(..., description="Total amount for this category")


class CategoryBreakdown(BaseModel):
    income: List[CategoryBreakdownItem] = Field(default_factory=list)
    expense: List[CategoryBreakdownItem] = Field(default_factory=list)


class Totals(BaseModel):
    income: Decimal = Field(..., description="Total income for period")
    expense: Decimal = Field(..., description="Total expenses for period")
    net: Decimal = Field(..., description="Net amount (income - expense)")


class TransactionSummary(BaseModel):
    id: int
    description: str
    amount: Decimal
    date: date_type
    category_name: str


class Metrics(BaseModel):
    average_daily_net: Decimal = Field(...,
                                       description="Average daily net amount")
    average_daily_income: Decimal = Field(...,
                                          description="Average daily income")
    average_daily_expense: Decimal = Field(...,
                                           description="Average daily expense")
    largest_expense: Optional[TransactionSummary] = Field(
        None, description="Largest expense transaction")
    largest_income: Optional[TransactionSummary] = Field(
        None, description="Largest income transaction")


class SummaryResponse(BaseModel):
    totals: Totals
    category_breakdown: CategoryBreakdown
    metrics: Metrics


class SummaryQueryParams(BaseModel):
    """Query parameters for summary endpoint."""
    from_date: Optional[date_type] = Field(
        None, description="Start date for summary")
    to_date: Optional[date_type] = Field(
        None, description="End date for summary")
    category_id: Optional[int] = Field(
        None, description="Filter by category ID")
