from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Index,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.db import Base


class SpendEntry(Base):
    __tablename__ = "spend_entries"

    id = Column(Integer, primary_key=True, index=True)

    trip_id = Column(
        Integer,
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reservation_id = Column(
        Integer,
        ForeignKey("reservations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")

    occurred_at = Column(DateTime(timezone=True), nullable=False)

    description = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    trip = relationship("Trip", backref="spend_entries")
    reservation = relationship("Reservation", backref="spend_entries")

    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_spend_entries_amount_nonnegative"),
        Index("ix_spend_entries_trip_occurred_at", "trip_id", "occurred_at"),
        Index("ix_spend_entries_trip_currency", "trip_id", "currency"),
    )

    def __repr__(self) -> str:
        return (
            f"<SpendEntry id={self.id} trip_id={self.trip_id} "
            f"amount={self.amount} {self.currency}>"
        )
