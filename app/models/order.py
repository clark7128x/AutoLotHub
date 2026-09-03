import uuid
from sqlalchemy import Column, Enum as SQLEnum, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    DELIVERED = "DELIVERED"

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    car_lot_id = Column(UUID(as_uuid=True), ForeignKey("car_lots.id"), unique=True, nullable=False)
    dealer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(OrderStatus, name="orderstatus_enum"), default=OrderStatus.PENDING, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    car_lot = relationship("CarLot", back_populates="order")
    dealer = relationship("User", back_populates="orders")
