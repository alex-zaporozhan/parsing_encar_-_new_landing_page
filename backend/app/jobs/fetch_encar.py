"""
ENCAR list API (разведка):

- База: https://api.encar.com (см. encarCommons.RYVUSS_BASE_END_POINT на www.encar.com).
- Листинг иностранных авто: GET /search/car/list/premium
- Параметры: ``q`` — запрос Ryvuss, ``sr`` — ``|{Sort}|{skip}|{limit}|`` (см. search.main.abstract.js).
- Счётчик только: ``count=true`` возвращает ``{"Count": N}``.

Поле ``external_id`` — строка ``Id`` из ``SearchResults[]`` (тот же id в URL карточки на fem.encar.com).

Ссылка на карточку: ``settings.encar_detail_url_template`` (по умолчанию fem.encar.com, не legacy fc_cardetailview.do).
"""

from __future__ import annotations

import json
import logging
import sys
import time
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal, init_db
from app.models import Vehicle

logger = logging.getLogger(__name__)

def _parse_year(item: dict[str, Any]) -> int:
    fy = item.get("FormYear")
    if fy is not None:
        s = str(fy).strip()
        if len(s) >= 4 and s[:4].isdigit():
            return int(s[:4])
    y = item.get("Year")
    if y is None:
        return 2000
    try:
        yi = int(float(y))
    except (TypeError, ValueError):
        return 2000
    if yi > 100_000:  # YYYYMM... из API
        return yi // 100
    if yi >= 1900:
        return yi
    return 2000


def _price_to_krw_won(price_manwon: Any) -> int:
    """Цена в ответе API в 만원 (10 000 KRW)."""
    try:
        p = float(price_manwon)
    except (TypeError, ValueError):
        return 0
    return int(round(p * 10000))


def _model_line(item: dict[str, Any]) -> str:
    m = (item.get("Model") or "").strip()
    badge = (item.get("Badge") or "").strip()
    if badge and badge not in m:
        return f"{m} {badge}".strip()
    return m or "Unknown"


def _photo_urls(item: dict[str, Any]) -> list[str]:
    base = settings.encar_photo_base.rstrip("/")
    out: list[str] = []
    for ph in item.get("Photos") or []:
        loc = ph.get("location")
        if isinstance(loc, str) and loc.startswith("/"):
            out.append(f"{base}{loc}")
    if not out:
        photo = item.get("Photo")
        if isinstance(photo, str) and photo:
            suffix = "001.jpg"
            out.append(f"{base}{photo}{suffix}")
    return out


def _fetch_page(client: httpx.Client, skip: int, limit: int) -> dict[str, Any]:
    # Формат как в search.main.abstract.js: ['', sort, skip, limit].join('|') → |ModifiedDate|0|20
    sr = f"|{settings.encar_sort}|{skip}|{limit}"
    params = {"q": settings.encar_search_query, "sr": sr}
    r = client.get(
        settings.encar_list_url,
        params=params,
        timeout=60.0,
    )
    r.raise_for_status()
    return r.json()


def upsert_vehicle(db: Session, payload: dict[str, Any], now_iso: str) -> None:
    eid = str(payload.get("Id", "")).strip()
    if not eid:
        return

    year = _parse_year(payload)
    if year <= 0:
        year = 2000

    mileage = payload.get("Mileage")
    mileage_km: int | None
    try:
        mileage_km = int(float(mileage)) if mileage is not None else None
    except (TypeError, ValueError):
        mileage_km = None

    price_amount = _price_to_krw_won(payload.get("Price"))
    if price_amount <= 0:
        price_amount = 1

    make = (payload.get("Manufacturer") or "Unknown").strip() or "Unknown"
    model = _model_line(payload)
    photos = _photo_urls(payload)
    photos_json = json.dumps(photos, ensure_ascii=False)
    source_url = settings.encar_detail_url_template.format(car_id=eid)

    row = {
        "external_id": eid,
        "make": make,
        "model": model,
        "year": year,
        "mileage_km": mileage_km,
        "price_amount": price_amount,
        "price_currency": "KRW",
        "photos_json": photos_json,
        "source_url": source_url,
        "fetched_at": now_iso,
        "updated_at": now_iso,
    }

    existing = db.execute(select(Vehicle).where(Vehicle.external_id == eid)).scalar_one_or_none()
    if existing is None:
        row["created_at"] = now_iso
        db.add(Vehicle(**row))
    else:
        existing.make = row["make"]
        existing.model = row["model"]
        existing.year = row["year"]
        existing.mileage_km = row["mileage_km"]
        existing.price_amount = row["price_amount"]
        existing.price_currency = row["price_currency"]
        existing.photos_json = row["photos_json"]
        existing.source_url = row["source_url"]
        existing.fetched_at = row["fetched_at"]
        existing.updated_at = row["updated_at"]


def run_fetch() -> int:
    """Загрузка страниц листинга и upsert в SQLite. Возвращает число обработанных объявлений."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    init_db()
    now_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    headers = {"User-Agent": settings.encar_user_agent, "Accept": "application/json"}
    total_processed = 0
    page_size = max(1, settings.encar_page_size)
    max_pages = max(1, settings.encar_max_pages)

    with httpx.Client(headers=headers, follow_redirects=True) as client:
        for page_idx in range(max_pages):
            skip = page_idx * page_size
            try:
                time.sleep(settings.encar_request_delay_sec)
                data = _fetch_page(client, skip, page_size)
            except Exception as e:
                logger.exception(
                    "encar_page_fetch_failed",
                    extra={"skip": skip, "limit": page_size, "error": str(e)},
                )
                continue

            results = data.get("SearchResults") or []
            if not results:
                logger.info("encar_no_more_results", extra={"page": page_idx})
                break

            db = SessionLocal()
            try:
                for item in results:
                    try:
                        if not isinstance(item, dict):
                            continue
                        upsert_vehicle(db, item, now_iso)
                        total_processed += 1
                    except Exception as e:
                        logger.exception(
                            "encar_item_failed",
                            extra={"external_id": item.get("Id"), "error": str(e)},
                        )
                db.commit()
            except Exception as e:
                logger.exception("encar_db_commit_failed", extra={"error": str(e)})
                db.rollback()
            finally:
                db.close()

    logger.info("encar_fetch_done", extra={"processed": total_processed})
    return total_processed


def main() -> None:
    n = run_fetch()
    sys.exit(0 if n >= 0 else 1)


if __name__ == "__main__":
    main()
