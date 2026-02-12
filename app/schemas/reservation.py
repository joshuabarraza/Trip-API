from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional, List

from pydantic import BaseModel, Field


# Pydantic v1/v2 compatibility (FastAPI can be either)
try:
    from pydantic import ConfigDict, field_validator  # type: ignore
    PYDANTIC_V2 = True
except Exception:  # pragma: no cover
    from pydantic import validator  # type: ignore
    PYDANTIC_V2 = False


ALLOWED_TYPES = {"lodging", "flight", "car", "train", "activity", "restaurant", "other"}
ALLOWED_STATUSES = {"planned", "booked", "canceled"}


class ReservationBase(BaseModel):
    type: str = Field(..., description="lodging|flight|car|train|activity|restaurant|other")
    status: str = Field(default="planned", description="planned|booked|canceled")

    title: str = Field(..., max_length=200)
    provider: Optional[str] = Field(default=None, max_length=120)
    confirmation_code: Optional[str] = Field(default=None, max_length=80)

    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    timezone: Optional[str] = Field(default=None, max_length=64)

    location_text: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = None

    estimated_cost_amount: Optional[Decimal] = Field(default=None, ge=0)
    estimated_cost_currency: str = Field(default="USD", min_length=3, max_length=3)

    meta: Dict[str, Any] = Field(default_factory=dict)

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)

        @field_validator("type")
        @classmethod
        def validate_type(cls, v: str) -> str:
            v = v.strip().lower()
            if v not in ALLOWED_TYPES:
                raise ValueError(f"type must be one of: {sorted(ALLOWED_TYPES)}")
            return v

        @field_validator("status")
        @classmethod
        def validate_status(cls, v: str) -> str:
            v = v.strip().lower()
            if v not in ALLOWED_STATUSES:
                raise ValueError(f"status must be one of: {sorted(ALLOWED_STATUSES)}")
            return v

        @field_validator("estimated_cost_currency")
        @classmethod
        def validate_currency(cls, v: str) -> str:
            v = v.strip().upper()
            if len(v) != 3:
                raise ValueError("estimated_cost_currency must be a 3-letter code (e.g., USD)")
            return v

        @field_validator("end_at")
        @classmethod
        def validate_dates(cls, end_at: Optional[datetime], info):
            start_at = info.data.get("start_at")
            if start_at and end_at and end_at < start_at:
                raise ValueError("end_at must be >= start_at")
            return end_at

    else:
        class Config:
            orm_mode = True

        @validator("type")
        def validate_type(cls, v: str) -> str:
            v = v.strip().lower()
            if v not in ALLOWED_TYPES:
                raise ValueError(f"type must be one of: {sorted(ALLOWED_TYPES)}")
            return v

        @validator("status")
        def validate_status(cls, v: str) -> str:
            v = v.strip().lower()
            if v not in ALLOWED_STATUSES:
                raise ValueError(f"status must be one of: {sorted(ALLOWED_STATUSES)}")
            return v

        @validator("estimated_cost_currency")
        def validate_currency(cls, v: str) -> str:
            v = v.strip().upper()
            if len(v) != 3:
                raise ValueError("estimated_cost_currency must be a 3-letter code (e.g., USD)")
            return v

        @validator("end_at")
        def validate_dates(cls, end_at: Optional[datetime], values):
            start_at = values.get("start_at")
            if start_at and end_at and end_at < start_at:
                raise ValueError("end_at must be >= start_at")
            return end_at


class ReservationCreate(ReservationBase):
    # same fields, but keep it explicit for readability/resume
    pass


class ReservationUpdate(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None

    title: Optional[str] = Field(default=None, max_length=200)
    provider: Optional[str] = Field(default=None, max_length=120)
    confirmation_code: Optional[str] = Field(default=None, max_length=80)

    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    timezone: Optional[str] = Field(default=None, max_length=64)

    location_text: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = None

    estimated_cost_amount: Optional[Decimal] = Field(default=None, ge=0)
    estimated_cost_currency: Optional[str] = Field(default=None, min_length=3, max_length=3)

    meta: Optional[Dict[str, Any]] = None

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)

        @field_validator("type")
        @classmethod
        def validate_type(cls, v: Optional[str]) -> Optional[str]:
            if v is None:
                return v
            v = v.strip().lower()
            if v not in ALLOWED_TYPES:
                raise ValueError(f"type must be one of: {sorted(ALLOWED_TYPES)}")
            return v

        @field_validator("status")
        @classmethod
        def validate_status(cls, v: Optional[str]) -> Optional[str]:
            if v is None:
                return v
            v = v.strip().lower()
            if v not in ALLOWED_STATUSES:
                raise ValueError(f"status must be one of: {sorted(ALLOWED_STATUSES)}")
            return v

        @field_validator("estimated_cost_currency")
        @classmethod
        def validate_currency(cls, v: Optional[str]) -> Optional[str]:
            if v is None:
                return v
            v = v.strip().upper()
            if len(v) != 3:
                raise ValueError("estimated_cost_currency must be a 3-letter code (e.g., USD)")
            return v

        @field_validator("end_at")
        @classmethod
        def validate_dates(cls, end_at: Optional[datetime], info):
            start_at = info.data.get("start_at")
            if start_at and end_at and end_at < start_at:
                raise ValueError("end_at must be >= start_at")
            return end_at

    else:
        class Config:
            orm_mode = True

        @validator("type")
        def validate_type(cls, v: Optional[str]) -> Optional[str]:
            if v is None:
                return v
            v = v.strip().lower()
            if v not in ALLOWED_TYPES:
                raise ValueError(f"type must be one of: {sorted(ALLOWED_TYPES)}")
            return v

        @validator("status")
        def validate_status(cls, v: Optional[str]) -> Optional[str]:
            if v is None:
                return v
            v = v.strip().lower()
            if v not in ALLOWED_STATUSES:
                raise ValueError(f"status must be one of: {sorted(ALLOWED_STATUSES)}")
            return v

        @validator("estimated_cost_currency")
        def validate_currency(cls, v: Optional[str]) -> Optional[str]:
            if v is None:
                return v
            v = v.strip().upper()
            if len(v) != 3:
                raise ValueError("estimated_cost_currency must be a 3-letter code (e.g., USD)")
            return v

        @validator("end_at")
        def validate_dates(cls, end_at: Optional[datetime], values):
            start_at = values.get("start_at")
            if start_at and end_at and end_at < start_at:
                raise ValueError("end_at must be >= start_at")
            return end_at


class ReservationOut(ReservationBase):
    id: int
    trip_id: int
    created_at: datetime
    updated_at: datetime

class CurrencyTotal(BaseModel):
    currency: str = Field(..., min_length=3, max_length=3, examples=["USD"])
    total: Decimal = Field(..., examples=["1240.50"])

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


class ReservationSummaryOut(BaseModel):
    trip_id: int
    by_status: Dict[str, int] = Field(
        default_factory=dict,
        description="Counts of reservations grouped by status",
        examples=[{"planned": 1, "booked": 4, "canceled": 0}],
    )
    by_type: Dict[str, int] = Field(
        default_factory=dict,
        description="Counts of reservations grouped by type",
        examples=[{"lodging": 2, "flight": 1, "activity": 2}],
    )
    estimated_totals: List[CurrencyTotal] = Field(
        default_factory=list,
        description="Sum of estimated_cost_amount grouped by currency (null amounts ignored)",
        examples=[[{"currency": "USD", "total": "1240.50"}]],
    )

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True