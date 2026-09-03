from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.car_lot import CarLotDTO, CarLotCreate, CarLotUpdate, VINDecodeRequest, ExternalCarDataDTO
from app.models.car_lot import CarLot, CarStatus
from app.models.user import User
from app.api.dependencies.auth import get_current_user, require_role
from app.services.car_lot import CarLotService
from app.repositories.car_lot import CarLotRepository
from app.external_services.vin_decoder import vin_decoder_service
from app.exceptions import BusinessLogicError

router = APIRouter()

def get_car_service(db: AsyncSession = Depends(get_db)) -> CarLotService:
    return CarLotService(CarLotRepository(db))

@router.get("", response_model=List[CarLotDTO])
async def read_cars(
    limit: int = 100,
    offset: int = 0,
    status: Optional[CarStatus] = None,
    service: CarLotService = Depends(get_car_service),
    current_user: User = Depends(get_current_user)
):
    return await service.get_cars(limit=limit, offset=offset, status=status)

@router.post("/decode-vin", response_model=ExternalCarDataDTO)
async def decode_vin(
    request: VINDecodeRequest,
    current_user: User = Depends(require_role(["Admin", "Manager"]))
):
    return await vin_decoder_service.decode_vin(request.vin)

@router.post("", response_model=CarLotDTO, status_code=status.HTTP_201_CREATED)
async def create_car(
    car_in: CarLotCreate,
    service: CarLotService = Depends(get_car_service),
    current_user: User = Depends(require_role(["Admin", "Manager"]))
):
    return await service.create_car(car_in)

@router.patch("/{car_id}", response_model=CarLotDTO)
async def update_car(
    car_id: UUID,
    car_in: CarLotUpdate,
    service: CarLotService = Depends(get_car_service),
    current_user: User = Depends(require_role(["Admin", "Manager"]))
):
    try:
        return await service.update_car(car_id, car_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(
    car_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    car = await db.get(CarLot, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car lot not found")
    await db.delete(car)
    await db.commit()
    return None
