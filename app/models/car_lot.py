import uuid
from sqlalchemy import Column, String, SmallInteger, Numeric, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class CarStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"

class CarLot(Base):
    __tablename__ = "car_lots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vin = Column(String(17), unique=True, index=True, nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(SmallInteger, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLEnum(CarStatus, name="carstatus_enum"), default=CarStatus.AVAILABLE, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("Order", back_populates="car_lot", uselist=False)
