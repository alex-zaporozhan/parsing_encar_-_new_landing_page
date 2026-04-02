"""Нормализация legacy URL карточки ENCAR."""

from app.encar_urls import resolve_public_detail_url


def test_legacy_fc_rewritten_to_fem() -> None:
    legacy = "https://www.encar.com/fc/fc_cardetailview.do?carId=40704612"
    out = resolve_public_detail_url(legacy, "40704612")
    assert out == "https://fem.encar.com/cars/detail/40704612"


def test_legacy_without_www_rewritten() -> None:
    legacy = "https://encar.com/fc/fc_cardetailview.do?carId=40704612"
    out = resolve_public_detail_url(legacy, "40704612")
    assert out == "https://fem.encar.com/cars/detail/40704612"


def test_fem_url_unchanged() -> None:
    fem = "https://fem.encar.com/cars/detail/40704612"
    assert resolve_public_detail_url(fem, "40704612") == fem


def test_empty_stored_uses_template() -> None:
    assert resolve_public_detail_url("", "99") == "https://fem.encar.com/cars/detail/99"
