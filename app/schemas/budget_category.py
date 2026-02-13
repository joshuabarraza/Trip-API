from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

try:
    from pydantic import ConfigDict
    PYDANTIC_V2 = True
except Exception:
    PYDANTIC_V2 = False


class BudgetCategoryCreate(BaseModel):
    name: str = Field(..., max_length=80)
    planned_amount: Optional[Decimal] = Field(default=None, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


class BudgetCategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=80)
    planned_amount: Optional[Decimal] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


class BudgetCategoryOut(BaseModel):
    id: int
    trip_id: int
    name: str
    planned_amount: Optional[Decimal]
    currency: str
    created_at: datetime
    updated_at: datetime

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True
