from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.deps import get_db
from app.middleware.auth import require_api_key
from app.middleware.rate_limit import limiter
from app.models.spend_entry import SpendEntry
from app.models.trip import Trip
from app.schemas.spend_entry import SpendCurrencyTotal, SpendSummaryOut

router = APIRouter(
    prefix="/v1",
    tags=["spend-entries"],
    dependencies=[Depends(require_api_key)],
)

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
