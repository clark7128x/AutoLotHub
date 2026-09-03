from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.car_lot import CarLot, CarStatus
from typing import List, Optional

class CarLotRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[CarStatus] = None,
    ) -> List[CarLot]:
        stmt = select(CarLot)
        if status is not None:
            stmt = stmt.where(CarLot.status == status)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, car_id: UUID) -> Optional[CarLot]:
        stmt = select(CarLot).where(CarLot.id == car_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, car: CarLot) -> CarLot:
        self.session.add(car)
        await self.session.flush()
        await self.session.refresh(car)
        return car

    async def update(self, car: CarLot) -> CarLot:
        await self.session.flush()
        await self.session.refresh(car)
        return car
