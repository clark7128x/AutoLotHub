from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.order import OrderDTO, OrderCreate, OrderStatusUpdate
from app.models.user import User
from app.api.dependencies.auth import get_current_user, require_role
from app.services.order import OrderService
from app.repositories.order import OrderRepository
from app.exceptions import BusinessLogicError

router = APIRouter()

def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(OrderRepository(db))

def is_user_dealer(user: User) -> bool:
    return any(role.name == "Dealer" for role in user.roles)

@router.get("", response_model=List[OrderDTO])
async def read_orders(
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user)
):
    is_dealer = is_user_dealer(current_user)
    return await service.get_orders(is_dealer=is_dealer, current_user_id=current_user.id)

@router.post("", response_model=OrderDTO, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(require_role(["Dealer"]))
):
    return await service.create_order(order_data=order_in, dealer_id=current_user.id)

@router.patch("/{order_id}/status", response_model=OrderDTO)
async def update_order_status(
    order_id: UUID,
    status_update: OrderStatusUpdate,
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(require_role(["Admin", "Manager"]))
):
    try:
        return await service.update_order_status(order_id, status_update.status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))

