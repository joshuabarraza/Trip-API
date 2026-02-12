from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripOut
from app.middleware.auth import require_api_key

router = APIRouter(
    prefix = "/v1/trips",
    tags = ["trips"],
    dependencies = [Depends(require_api_key)]
)



@router.post("", response_model = TripOut, status_code = 201)
def create_trip(payload: TripCreate, db: Session = Depends(get_db)):
    trip = Trip(
        title = payload.title,
        destination = payload.destination,
        start_date = payload.start_date,
        end_date = payload.end_date,
        status = payload.status,
        tags = payload.tags
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("", response_model = List[TripOut])
def list_trips(
    limit: int = Query(default = 20, ge = 1, le = 100),
    offset: int = Query(default = 0, ge = 0),
    db: Session = Depends(get_db)
):
    trips = (
        db.query(Trip)
        .order_by(Trip.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return trips
