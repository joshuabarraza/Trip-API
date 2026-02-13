from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.deps import get_db
from app.middleware.auth import require_api_key
from app.middleware.rate_limit import limiter
from app.models.budget_category import BudgetCategory
from app.models.trip import Trip
from app.schemas.budget_category import BudgetCategoryCreate, BudgetCategoryOut, BudgetCategoryUpdate

router = APIRouter(
    prefix="/v1",
    tags=["budget-categories"],
    dependencies=[Depends(require_api_key)],
)


@router.post("/trips/{trip_id}/budget-categories", response_model=BudgetCategoryOut, status_code=201)
@limiter.limit("30/minute")
def create_budget_category(request: Request, trip_id: int, payload: BudgetCategoryCreate, db: Session = Depends(get_db)):
    trip_exists = db.query(Trip.id).filter(Trip.id == trip_id).first()
    if not trip_exists:
        raise HTTPException(status_code=404, detail="Trip not found")

    existing = (
        db.query(BudgetCategory.id)
        .filter(BudgetCategory.trip_id == trip_id, BudgetCategory.name == payload.name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Category name already exists for this trip")

    cat = BudgetCategory(
        trip_id=trip_id,
        name=payload.name,
        planned_amount=payload.planned_amount,
        currency=payload.currency.strip().upper(),
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.get("/trips/{trip_id}/budget-categories", response_model=List[BudgetCategoryOut])
@limiter.limit("30/minute")
def list_budget_categories(
    request: Request,
    trip_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    trip_exists = db.query(Trip.id).filter(Trip.id == trip_id).first()
    if not trip_exists:
        raise HTTPException(status_code=404, detail="Trip not found")

    return (
        db.query(BudgetCategory)
        .filter(BudgetCategory.trip_id == trip_id)
        .order_by(BudgetCategory.name.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.patch("/budget-categories/{category_id}", response_model=BudgetCategoryOut)
@limiter.limit("30/minute")
def update_budget_category(request: Request, category_id: int, payload: BudgetCategoryUpdate, db: Session = Depends(get_db)):
    cat = db.query(BudgetCategory).filter(BudgetCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Budget category not found")

    data = payload.dict(exclude_unset=True) if hasattr(payload, "dict") else payload.model_dump(exclude_unset=True)

    if "currency" in data and data["currency"] is not None:
        data["currency"] = data["currency"].strip().upper()

    if "name" in data and data["name"] is not None:
        existing = (
            db.query(BudgetCategory.id)
            .filter(BudgetCategory.trip_id == cat.trip_id, BudgetCategory.name == data["name"], BudgetCategory.id != cat.id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=409, detail="Category name already exists for this trip")

    for k, v in data.items():
        setattr(cat, k, v)

    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/budget-categories/{category_id}", status_code=204)
@limiter.limit("30/minute")
def delete_budget_category(request: Request, category_id: int, db: Session = Depends(get_db)):
    cat = db.query(BudgetCategory).filter(BudgetCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Budget category not found")

    db.delete(cat)
    db.commit()
    return None
