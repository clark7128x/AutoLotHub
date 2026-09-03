from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal
from app.models.car_lot import CarStatus

class CarLotCreate(BaseModel):
    vin: str
    make: str
    model: str
    year: int
    price: Decimal

class CarLotUpdate(BaseModel):
    price: Optional[Decimal] = None
    status: Optional[CarStatus] = None

class CarLotDTO(BaseModel):
    id: UUID
    vin: str
    make: str
    model: str
    year: int
    price: Decimal
    status: CarStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ExternalCarDataDTO(BaseModel):
    vin: str
    make: str
    model: str
    year: int
    country: str
    history_status: str
    damage: Optional[str] = None
    engine: Optional[str] = None

class VINDecodeRequest(BaseModel):
    vin: str
