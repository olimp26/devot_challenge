"""Seed global categories

Revision ID: 8917c0b9530b
Revises: fabbd50d85f2
Create Date: 2025-08-03 18:45:16.624867

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, DateTime, Enum


# revision identifiers, used by Alembic.
revision: str = '8917c0b9530b'
down_revision: Union[str, None] = 'fabbd50d85f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Define the categories table structure for data insertion
    categories_table = table('categories',
                             column('name', String),
                             column('category_type', String),
                             column('user_id', Integer),
                             column('last_changed', DateTime)
                             )

    # Global income categories
    income_categories = [
        "Salary",
        "Freelancing",
        "Investment Returns",
        "Rental Income",
        "Business Income",
        "Other Income"
    ]

    # Global expense categories
    expense_categories = [
        "Food & Dining",
        "Transportation",
        "Shopping",
        "Entertainment",
        "Bills & Utilities",
        "Healthcare",
        "Education",
        "Travel",
        "Housing",
        "Insurance",
        "Other Expenses"
    ]

    # Insert income categories
    for name in income_categories:
        op.execute(
            categories_table.insert().values(
                name=name,
                category_type='income',
                user_id=None,
                last_changed=sa.func.current_timestamp()
            )
        )

    # Insert expense categories
    for name in expense_categories:
        op.execute(
            categories_table.insert().values(
                name=name,
                category_type='expense',
                user_id=None,
                last_changed=sa.func.current_timestamp()
            )
        )


def downgrade() -> None:
    # Remove all global categories (where user_id is NULL)
    op.execute("DELETE FROM categories WHERE user_id IS NULL")
