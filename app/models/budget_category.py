from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Index,
    UniqueConstraint,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.db import Base


class BudgetCategory(Base):
    __tablename__ = "budget_categories"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(80), nullable=False)  # "Lodging", "Flights", etc.
    planned_amount = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(3), nullable=False, default="USD")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    trip = relationship("Trip", backref="budget_categories")

    __table_args__ = (
        UniqueConstraint("trip_id", "name", name="uq_budget_categories_trip_name"),
        CheckConstraint("(planned_amount IS NULL) OR (planned_amount >= 0)", name="ck_budget_categories_planned_nonnegative"),
        Index("ix_budget_categories_trip_name", "trip_id", "name"),
    )

    def __repr__(self) -> str:
        return f"<BudgetCategory id={self.id} trip_id={self.trip_id} name={self.name!r}>"
