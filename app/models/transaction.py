from sqlalchemy import Column, Integer, Text, DECIMAL, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    date = Column(Date, default=func.current_date(), nullable=False)
    last_changed = Column(DateTime(timezone=True),
                          server_default=func.current_timestamp(), nullable=False)

    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    @property
    def category_name(self) -> str:
        return self.category.name if self.category else ""

    @property
    def category_type(self) -> str:
        return self.category.category_type.value if self.category else ""
