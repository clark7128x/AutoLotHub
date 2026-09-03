from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.order import OrderStatus

class OrderCreate(BaseModel):
    car_lot_id: UUID
    notes: Optional[str] = None

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class OrderDTO(BaseModel):
    id: UUID
    car_lot_id: UUID
    dealer_id: UUID
    status: OrderStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
