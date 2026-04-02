from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    make: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str] = mapped_column(String(512), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    mileage_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    price_currency: Mapped[str] = mapped_column(String(8), nullable=False, default="KRW")
    photos_json: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    fetched_at: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)
