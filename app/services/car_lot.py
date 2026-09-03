from uuid import UUID
from app.repositories.car_lot import CarLotRepository
from app.models.car_lot import CarLot, CarStatus
from app.schemas.car_lot import CarLotCreate, CarLotUpdate
from typing import List, Optional

class CarLotService:
    def __init__(self, repository: CarLotRepository):
        self.repository = repository

    async def get_cars(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[CarStatus] = None,
    ) -> List[CarLot]:
        return await self.repository.get_all(limit=limit, offset=offset, status=status)
        
    async def get_car_by_id(self, car_id: UUID) -> CarLot:
        car = await self.repository.get_by_id(car_id)
        if not car:
            raise ValueError("Car lot not found")
        return car

    async def create_car(self, car_data: CarLotCreate) -> CarLot:
        new_car = CarLot(**car_data.model_dump())
        return await self.repository.create(new_car)

    async def update_car(self, car_id: UUID, update_data: CarLotUpdate) -> CarLot:
        car = await self.repository.get_by_id(car_id)
        if not car:
            raise ValueError("Car lot not found")
        if update_data.price is not None:
            car.price = update_data.price
        if update_data.status is not None:
            car.status = update_data.status
        return await self.repository.update(car)
