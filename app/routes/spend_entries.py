from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.deps import get_db
from app.middleware.auth import require_api_key
from app.middleware.rate_limit import limiter
from app.models.budget_category import BudgetCategory
from app.models.reservation import Reservation
from app.models.spend_entry import SpendEntry
from app.models.trip import Trip
from app.schemas.spend_entry import (
    SpendCurrencyTotal,
    SpendEntryCreate,
    SpendEntryOut,
    SpendEntryUpdate,
    SpendSummaryOut,
)

router = APIRouter(
    prefix="/v1",
    tags=["spend-entries"],
    dependencies=[Depends(require_api_key)],
)


@router.post("/trips/{trip_id}/spend-entries", response_model=SpendEntryOut, status_code=201)
@limiter.limit("30/minute")
def create_spend_entry(
    request: Request,
    trip_id: int,
    payload: SpendEntryCreate,
    db: Session = Depends(get_db),
):
    trip_exists = db.query(Trip.id).filter(Trip.id == trip_id).first()
    if not trip_exists:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Validate reservation_id (optional) belongs to this trip
    if payload.reservation_id is not None:
        res = (
            db.query(Reservation.id, Reservation.trip_id)
            .filter(Reservation.id == payload.reservation_id)
            .first()
        )
        if not res:
            raise HTTPException(status_code=404, detail="Reservation not found")
        if res.trip_id != trip_id:
            raise HTTPException(status_code=400, detail="reservation_id does not belong to this trip")

    # Validate category_id (optional) belongs to this trip
    if getattr(payload, "category_id", None) is not None:
        cat = (
            db.query(BudgetCategory.id, BudgetCategory.trip_id)
            .filter(BudgetCategory.id == payload.category_id)
            .first()
        )
        if not cat:
            raise HTTPException(status_code=404, detail="Budget category not found")
        if cat.trip_id != trip_id:
            raise HTTPException(status_code=400, detail="category_id does not belong to this trip")

    entry = SpendEntry(
        trip_id=trip_id,
        reservation_id=payload.reservation_id,
        category_id=getattr(payload, "category_id", None),
        amount=payload.amount,
        currency=payload.currency,
        occurred_at=payload.occurred_at,
        description=payload.description,
        notes=payload.notes,
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/trips/{trip_id}/spend-entries", response_model=List[SpendEntryOut])
@limiter.limit("30/minute")
def list_spend_entries(
    request: Request,
    trip_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    currency: Optional[str] = Query(default=None, description="3-letter currency code, e.g. USD"),
    reservation_id: Optional[int] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    from_dt: Optional[datetime] = Query(default=None, alias="from", description="occurred_at >= from"),
    to_dt: Optional[datetime] = Query(default=None, alias="to", description="occurred_at <= to"),
    db: Session = Depends(get_db),
):
    trip_exists = db.query(Trip.id).filter(Trip.id == trip_id).first()
    if not trip_exists:
        raise HTTPException(status_code=404, detail="Trip not found")

    q = db.query(SpendEntry).filter(SpendEntry.trip_id == trip_id)

    if currency:
        q = q.filter(SpendEntry.currency == currency.strip().upper())

    if reservation_id is not None:
        q = q.filter(SpendEntry.reservation_id == reservation_id)

    if category_id is not None:
        q = q.filter(SpendEntry.category_id == category_id)

    if from_dt:
        q = q.filter(SpendEntry.occurred_at >= from_dt)

    if to_dt:
        q = q.filter(SpendEntry.occurred_at <= to_dt)

    # Newest first (ledger view)
    q = q.order_by(desc(SpendEntry.occurred_at), desc(SpendEntry.id))

    return q.offset(offset).limit(limit).all()


@router.get("/spend-entries/{spend_entry_id}", response_model=SpendEntryOut)
@limiter.limit("30/minute")
def get_spend_entry(
    request: Request,
    spend_entry_id: int,
    db: Session = Depends(get_db),
):
    entry = db.query(SpendEntry).filter(SpendEntry.id == spend_entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Spend entry not found")
    return entry


@router.patch("/spend-entries/{spend_entry_id}", response_model=SpendEntryOut)
@limiter.limit("30/minute")
def update_spend_entry(
    request: Request,
    spend_entry_id: int,
    payload: SpendEntryUpdate,
    db: Session = Depends(get_db),
):
    entry = db.query(SpendEntry).filter(SpendEntry.id == spend_entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Spend entry not found")

    data = payload.dict(exclude_unset=True) if hasattr(payload, "dict") else payload.model_dump(exclude_unset=True)

    # Validate reservation_id update (optional)
    if "reservation_id" in data and data["reservation_id"] is not None:
        res = (
            db.query(Reservation.id, Reservation.trip_id)
            .filter(Reservation.id == data["reservation_id"])
            .first()
        )
        if not res:
            raise HTTPException(status_code=404, detail="Reservation not found")
        if res.trip_id != entry.trip_id:
            raise HTTPException(status_code=400, detail="reservation_id does not belong to this trip")

    # Validate category_id update (optional)
    if "category_id" in data:
        if data["category_id"] is None:
            # allow unsetting category
            pass
        else:
            cat = (
                db.query(BudgetCategory.id, BudgetCategory.trip_id)
                .filter(BudgetCategory.id == data["category_id"])
                .first()
            )
            if not cat:
                raise HTTPException(status_code=404, detail="Budget category not found")
            if cat.trip_id != entry.trip_id:
                raise HTTPException(status_code=400, detail="category_id does not belong to this trip")

    for key, value in data.items():
        setattr(entry, key, value)

    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/spend-entries/{spend_entry_id}", status_code=204)
@limiter.limit("30/minute")
def delete_spend_entry(
    request: Request,
    spend_entry_id: int,
    db: Session = Depends(get_db),
):
    entry = db.query(SpendEntry).filter(SpendEntry.id == spend_entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Spend entry not found")

    db.delete(entry)
    db.commit()
    return None


@router.get("/trips/{trip_id}/spend-entries/summary", response_model=SpendSummaryOut)
@limiter.limit("30/minute")
def spend_entries_summary(
    request: Request,
    trip_id: int,
    db: Session = Depends(get_db),
):
    trip_exists = db.query(Trip.id).filter(Trip.id == trip_id).first()
    if not trip_exists:
        raise HTTPException(status_code=404, detail="Trip not found")

    total_entries = (
        db.query(func.count(SpendEntry.id))
        .filter(SpendEntry.trip_id == trip_id)
        .scalar()
    ) or 0

    totals_rows = (
        db.query(
            SpendEntry.currency,
            func.coalesce(func.sum(SpendEntry.amount), 0),
        )
        .filter(SpendEntry.trip_id == trip_id)
        .group_by(SpendEntry.currency)
        .all()
    )

    totals_by_currency = [
        SpendCurrencyTotal(currency=currency, total=total)
        for currency, total in totals_rows
    ]

    return SpendSummaryOut(
        trip_id=trip_id,
        total_entries=total_entries,
        totals_by_currency=totals_by_currency,
    )
