from pydantic import BaseModel, Field


class PriceOut(BaseModel):
    amount: int
    currency: str


class VehicleOut(BaseModel):
    id: int
    make: str
    model: str
    year: int
    mileage_km: int | None
    price: PriceOut
    photos: list[str]
    source_url: str


class VehiclesPage(BaseModel):
    items: list[VehicleOut]
    total: int


class HealthOut(BaseModel):
    status: str = "ok"


class ErrorBody(BaseModel):
    detail: str
    code: str


class VehiclesQuery(BaseModel):
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
