from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field

try:
    from pydantic import ConfigDict
    PYDANTIC_V2 = True
except Exception:
    PYDANTIC_V2 = False


class SpendEntryCreate(BaseModel):
    reservation_id: Optional[int] = None
    amount: Decimal = Field(..., ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    occurred_at: datetime
    description: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = None

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


class SpendEntryUpdate(BaseModel):
    reservation_id: Optional[int] = None
    amount: Optional[Decimal] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    occurred_at: Optional[datetime] = None
    description: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = None

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


class SpendEntryOut(BaseModel):
    id: int
    trip_id: int
    reservation_id: Optional[int]
    amount: Decimal
    currency: str
    occurred_at: datetime
    description: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True

class SpendCurrencyTotal(BaseModel):
    currency: str = Field(..., min_length=3, max_length=3, examples=["USD"])
    total: Decimal = Field(..., examples=["420.50"])


class SpendSummaryOut(BaseModel):
    trip_id: int
    total_entries: int = Field(..., examples=[5])
    totals_by_currency: List[SpendCurrencyTotal] = Field(default_factory=list)

