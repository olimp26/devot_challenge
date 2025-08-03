"""
Summary service layer for handling financial summary business logic.
"""
from typing import List
from decimal import Decimal

from app.models.transaction import Transaction
from app.models.category import CategoryType
from app.schemas.summary import (
    SummaryResponse,
    SummaryQueryParams,
    Totals,
    CategoryBreakdown,
    CategoryBreakdownItem,
    Metrics,
    TransactionSummary
)
from app.schemas.transaction import TransactionQueryParams as TransactionFilters


class SummaryService:
    """Service class for financial summary-related business logic."""

    def __init__(self, transaction_service):
        self.transaction_service = transaction_service

    def get_user_summary(
        self,
        user_id: int,
        params: SummaryQueryParams
    ) -> SummaryResponse:
        transactions = self.transaction_service.get_all_user_transactions_for_summary(
            user_id=user_id,
            category_id=params.category_id,
            from_date=params.from_date,
            to_date=params.to_date
        )

        total_income = sum(
            t.amount for t in transactions
            if t.category.category_type == CategoryType.income
        )
        total_expense = sum(
            t.amount for t in transactions
            if t.category.category_type == CategoryType.expense
        )
        net_total = total_income - total_expense

        totals = Totals(
            income=total_income,
            expense=total_expense,
            net=net_total
        )

        category_breakdown = self._calculate_category_breakdown(transactions)

        metrics = self._calculate_metrics(transactions, params)

        return SummaryResponse(
            totals=totals,
            category_breakdown=category_breakdown,
            metrics=metrics
        )

    def _calculate_category_breakdown(self, transactions: List[Transaction]) -> CategoryBreakdown:
        income_breakdown = {}
        expense_breakdown = {}

        for transaction in transactions:
            category_name = transaction.category.name
            amount = transaction.amount

            if transaction.category.category_type == CategoryType.income:
                income_breakdown[category_name] = income_breakdown.get(
                    category_name, Decimal('0')) + amount
            else:
                expense_breakdown[category_name] = expense_breakdown.get(
                    category_name, Decimal('0')) + amount

        income_items = [
            CategoryBreakdownItem(category=name, total=total)
            for name, total in sorted(income_breakdown.items(), key=lambda x: x[1], reverse=True)
        ]
        expense_items = [
            CategoryBreakdownItem(category=name, total=total)
            for name, total in sorted(expense_breakdown.items(), key=lambda x: x[1], reverse=True)
        ]

        return CategoryBreakdown(
            income=income_items,
            expense=expense_items
        )

    def _calculate_metrics(self, transactions: List[Transaction], params: SummaryQueryParams) -> Metrics:
        if not transactions:
            return Metrics(
                average_daily_net=Decimal('0'),
                average_daily_income=Decimal('0'),
                average_daily_expense=Decimal('0'),
                largest_expense=None,
                largest_income=None
            )

        if params.from_date and params.to_date:
            days_in_period = (params.to_date - params.from_date).days + 1
        else:
            dates = [t.date for t in transactions]
            if dates:
                days_in_period = (max(dates) - min(dates)).days + 1
            else:
                days_in_period = 1

        income_transactions = [
            t for t in transactions if t.category.category_type == CategoryType.income]
        expense_transactions = [
            t for t in transactions if t.category.category_type == CategoryType.expense]

        total_income = sum((Decimal(str(t.amount))
                           for t in income_transactions), Decimal('0'))
        total_expense = sum((Decimal(str(t.amount))
                            for t in expense_transactions), Decimal('0'))

        days_decimal = Decimal(str(days_in_period))
        avg_daily_income = (total_income / days_decimal if days_in_period >
                            0 else Decimal('0')).quantize(Decimal('0.01'))
        avg_daily_expense = (total_expense / days_decimal if days_in_period >
                             0 else Decimal('0')).quantize(Decimal('0.01'))
        avg_daily_net = (avg_daily_income -
                         avg_daily_expense).quantize(Decimal('0.01'))

        largest_income = None
        largest_expense = None

        if income_transactions:
            largest_income_tx = max(
                income_transactions, key=lambda t: t.amount)
            largest_income = TransactionSummary(
                id=largest_income_tx.id,
                description=largest_income_tx.description,
                amount=largest_income_tx.amount,
                date=largest_income_tx.date,
                category_name=largest_income_tx.category.name
            )

        if expense_transactions:
            largest_expense_tx = max(
                expense_transactions, key=lambda t: t.amount)
            largest_expense = TransactionSummary(
                id=largest_expense_tx.id,
                description=largest_expense_tx.description,
                amount=largest_expense_tx.amount,
                date=largest_expense_tx.date,
                category_name=largest_expense_tx.category.name
            )

        return Metrics(
            average_daily_net=avg_daily_net,
            average_daily_income=avg_daily_income,
            average_daily_expense=avg_daily_expense,
            largest_expense=largest_expense,
            largest_income=largest_income
        )
