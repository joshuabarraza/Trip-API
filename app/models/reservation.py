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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db import Base


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)

    trip_id = Column(
        Integer,
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # keep simple string enums (validate in Pydantic)
    type = Column(String(32), nullable=False)      # lodging|flight|car|train|activity|restaurant|other
    status = Column(String(16), nullable=False, default="planned")  # planned|booked|canceled

    title = Column(String(200), nullable=False)
    provider = Column(String(120), nullable=True)
    confirmation_code = Column(String(80), nullable=True)

    # timezone-aware timestamps for itinerary + reminders
    start_at = Column(DateTime(timezone=True), nullable=True)
    end_at = Column(DateTime(timezone=True), nullable=True)
    timezone = Column(String(64), nullable=True)  # e.g., "America/Los_Angeles"

    location_text = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)

    # planning money (actual spend later via SpendEntry)
    estimated_cost_amount = Column(Numeric(12, 2), nullable=True)
    estimated_cost_currency = Column(String(3), nullable=False, default="USD")

    # flexible structured details per reservation type
    meta = Column(JSONB, nullable=False, default=dict)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    trip = relationship("Trip", backref="reservations")

    __table_args__ = (
        CheckConstraint(
            "(start_at IS NULL) OR (end_at IS NULL) OR (end_at >= start_at)",
            name="ck_reservations_end_after_start",
        ),
        CheckConstraint(
            "(estimated_cost_amount IS NULL) OR (estimated_cost_amount >= 0)",
            name="ck_reservations_estimated_cost_nonnegative",
        ),
        Index("ix_reservations_trip_start_at", "trip_id", "start_at"),
        Index("ix_reservations_trip_type", "trip_id", "type"),
        Index("ix_reservations_trip_status", "trip_id", "status"),
    )

    def __repr__(self) -> str:
        return (
            f"<Reservation id={self.id} trip_id={self.trip_id} "
            f"type={self.type} status={self.status} title={self.title!r}>"
        )
