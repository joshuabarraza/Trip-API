from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from app.deps import get_db
from app.middleware.auth import require_api_key
from app.middleware.rate_limit import limiter
from app.models.trip import Trip
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationCreate, ReservationOut, ReservationUpdate

from sqlalchemy import func
from app.schemas.reservation import ReservationSummaryOut, CurrencyTotal



router = APIRouter(
    prefix="/v1",
    tags=["reservations"],
    dependencies=[Depends(require_api_key)],
)


@router.post("/trips/{trip_id}/reservations", response_model=ReservationOut, status_code=201)
@limiter.limit("30/minute")
def create_reservation(
    request: Request,
    trip_id: int,
    payload: ReservationCreate,
    db: Session = Depends(get_db),
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    reservation = Reservation(
        trip_id=trip_id,
        type=payload.type,
        status=payload.status,
        title=payload.title,
        provider=payload.provider,
        confirmation_code=payload.confirmation_code,
        start_at=payload.start_at,
        end_at=payload.end_at,
        timezone=payload.timezone,
        location_text=payload.location_text,
        notes=payload.notes,
        estimated_cost_amount=payload.estimated_cost_amount,
        estimated_cost_currency=payload.estimated_cost_currency,
        meta=payload.meta,
    )

    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


@router.get("/trips/{trip_id}/reservations", response_model=List[ReservationOut])
@limiter.limit("30/minute")
def list_reservations(
    request: Request,
    trip_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    type: Optional[str] = Query(default=None, description="Filter by reservation type"),
    status: Optional[str] = Query(default=None, description="Filter by reservation status"),
    from_dt: Optional[datetime] = Query(default=None, alias="from", description="Filter start_at >= from"),
    to_dt: Optional[datetime] = Query(default=None, alias="to", description="Filter start_at <= to"),
    db: Session = Depends(get_db),
):
    # optional: keep behavior consistent by returning 404 if trip doesn't exist
    trip_exists = db.query(Trip.id).filter(Trip.id == trip_id).first()
    if not trip_exists:
        raise HTTPException(status_code=404, detail="Trip not found")

    q = db.query(Reservation).filter(Reservation.trip_id == trip_id)

    if type:
        q = q.filter(Reservation.type == type.strip().lower())

    if status:
        q = q.filter(Reservation.status == status.strip().lower())

    if from_dt:
        q = q.filter(Reservation.start_at >= from_dt)

    if to_dt:
        q = q.filter(Reservation.start_at <= to_dt)

    # Professional sort: itinerary first (nulls last), then newest created
    # Postgres supports NULLS LAST; SQLAlchemy uses .nulls_last()
    q = q.order_by(
        asc(Reservation.start_at).nulls_last(),
        desc(Reservation.created_at),
        desc(Reservation.id),
    )

    reservations = q.offset(offset).limit(limit).all()
    return reservations


@router.get("/reservations/{reservation_id}", response_model=ReservationOut)
@limiter.limit("30/minute")
def get_reservation(
    request: Request,
    reservation_id: int,
    db: Session = Depends(get_db),
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


@router.patch("/reservations/{reservation_id}", response_model=ReservationOut)
@limiter.limit("30/minute")
def update_reservation(
    request: Request,
    reservation_id: int,
    payload: ReservationUpdate,
    db: Session = Depends(get_db),
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    data = payload.dict(exclude_unset=True) if hasattr(payload, "dict") else payload.model_dump(exclude_unset=True)

    # Apply updates
    for key, value in data.items():
        setattr(reservation, key, value)

    db.commit()
    db.refresh(reservation)
    return reservation


@router.delete("/reservations/{reservation_id}", status_code=204)
@limiter.limit("30/minute")
def delete_reservation(
    request: Request,
    reservation_id: int,
    db: Session = Depends(get_db),
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    db.delete(reservation)
    db.commit()
    return None

@router.get("/trips/{trip_id}/reservations/summary", response_model=ReservationSummaryOut)
@limiter.limit("30/minute")
def reservation_summary(
    request: Request,
    trip_id: int,
    db: Session = Depends(get_db),
):
    # Ensure trip exists
    trip_exists = db.query(Trip.id).filter(Trip.id == trip_id).first()
    if not trip_exists:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Count by status
    status_rows = (
        db.query(Reservation.status, func.count(Reservation.id))
        .filter(Reservation.trip_id == trip_id)
        .group_by(Reservation.status)
        .all()
    )

    by_status = {status: count for status, count in status_rows}

    # Count by type
    type_rows = (
        db.query(Reservation.type, func.count(Reservation.id))
        .filter(Reservation.trip_id == trip_id)
        .group_by(Reservation.type)
        .all()
    )

    by_type = {rtype: count for rtype, count in type_rows}

    # Sum estimated cost grouped by currency (ignore null amounts)
    total_rows = (
        db.query(
            Reservation.estimated_cost_currency,
            func.coalesce(func.sum(Reservation.estimated_cost_amount), 0),
        )
        .filter(
            Reservation.trip_id == trip_id,
            Reservation.estimated_cost_amount.isnot(None),
        )
        .group_by(Reservation.estimated_cost_currency)
        .all()
    )

    estimated_totals = [
        CurrencyTotal(currency=currency, total=total)
        for currency, total in total_rows
    ]

    return ReservationSummaryOut(
        trip_id=trip_id,
        by_status=by_status,
        by_type=by_type,
        estimated_totals=estimated_totals,
    )
