"""Смоук API + CORS preflight (MR-1, MR-5 частично)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok() -> None:
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_vehicles_shape() -> None:
    r = client.get("/api/v1/vehicles?limit=5&offset=0")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data and "total" in data
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)
    if data["items"]:
        v = data["items"][0]
        for k in (
            "id",
            "make",
            "model",
            "year",
            "mileage_km",
            "price",
            "photos",
            "source_url",
        ):
            assert k in v
        assert "amount" in v["price"] and "currency" in v["price"]


def test_vehicles_validation_limit() -> None:
    r = client.get("/api/v1/vehicles?limit=201")
    assert r.status_code == 422
    body = r.json()
    assert body.get("code") == "VALIDATION_ERROR"
    assert "detail" in body


def test_vehicles_validation_offset() -> None:
    r = client.get("/api/v1/vehicles?offset=-1")
    assert r.status_code == 422
    assert r.json().get("code") == "VALIDATION_ERROR"


def test_cors_preflight_options() -> None:
    """OPTIONS + Access-Control-Request-Method (MR-1)."""
    r = client.options(
        "/api/v1/vehicles?limit=1",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code in (200, 204)
    assert r.headers.get("access-control-allow-origin") in (
        "http://localhost:3000",
        "*",
    )
