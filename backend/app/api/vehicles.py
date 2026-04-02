import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.encar_urls import resolve_public_detail_url
from app.models import Vehicle
from app.schemas import HealthOut, PriceOut, VehicleOut, VehiclesPage

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok")


@router.get("/vehicles", response_model=VehiclesPage)
def list_vehicles(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> VehiclesPage:
    try:
        total = db.execute(select(func.count()).select_from(Vehicle)).scalar_one()
        rows = (
            db.execute(
                select(Vehicle)
                .order_by(Vehicle.updated_at.desc())
                .offset(offset)
                .limit(limit),
            )
            .scalars()
            .all()
        )
    except Exception as e:
        logger.exception("vehicles_db_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=500,
            detail={"detail": "Database error", "code": "INTERNAL_ERROR"},
        ) from e

    items: list[VehicleOut] = []
    for v in rows:
        try:
            photos = json.loads(v.photos_json) if v.photos_json else []
            if not isinstance(photos, list):
                photos = []
        except json.JSONDecodeError:
            photos = []
        items.append(
            VehicleOut(
                id=v.id,
                make=v.make,
                model=v.model,
                year=v.year,
                mileage_km=v.mileage_km,
                price=PriceOut(amount=v.price_amount, currency=v.price_currency),
                photos=photos,
                source_url=resolve_public_detail_url(v.source_url, v.external_id),
            ),
        )
    return VehiclesPage(items=items, total=int(total or 0))
