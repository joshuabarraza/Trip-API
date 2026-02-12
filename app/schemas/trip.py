from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class TripCreate(BaseModel):
    title: str = Field(min_length = 1, max_length = 120)
    destination: Optional[str] = Field(default = None, max_length = 120)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = Field(default = "planning", max_length = 30)
    tags: List[str] = Field(default_factory = list)


class TripOut(BaseModel):
    id: int
    title: str
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str
    tags: List[str]

    class Config:
        from_attributes = True
