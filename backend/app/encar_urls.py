"""Нормализация ссылок на карточку ENCAR для ответа API."""

from __future__ import annotations

from app.config import settings


def resolve_public_detail_url(stored_url: str, external_id: str) -> str:
    """
    Legacy ``www.encar.com/fc/fc_cardetailview.do?carId=…`` снаружи часто отдаёт 502.
    В JSON для фронта всегда подменяем на актуальный шаблон (по умолчанию fem.encar.com),
    используя ``external_id`` (= Id из API ENCAR = carId в старой ссылке).
    """
    u = (stored_url or "").strip()
    ext = (external_id or "").strip()
    if ext and "fc_cardetailview.do" in u.lower():
        return settings.encar_detail_url_template.format(car_id=ext)
    if not u and ext:
        return settings.encar_detail_url_template.format(car_id=ext)
    return u
