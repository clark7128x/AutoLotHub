from uuid import UUID
from app.repositories.order import OrderRepository
from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate
from app.exceptions import BusinessLogicError
from typing import List

class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    async def get_orders(self, is_dealer: bool, current_user_id: UUID) -> List[Order]:
        dealer_id = current_user_id if is_dealer else None
        return await self.repository.get_all(dealer_id=dealer_id)

    async def get_order_by_id(self, order_id: UUID, is_dealer: bool, current_user_id: UUID) -> Order:
        dealer_id = current_user_id if is_dealer else None
        order = await self.repository.get_by_id(order_id, dealer_id=dealer_id)
        if not order:
            raise ValueError("Order not found or access denied")
        return order

    async def create_order(self, order_data: OrderCreate, dealer_id: UUID) -> Order:
        new_order = Order(
            car_lot_id=order_data.car_lot_id,
            dealer_id=dealer_id,
            notes=order_data.notes,
            status=OrderStatus.PENDING
        )
        return await self.repository.create(new_order)

    async def update_order_status(self, order_id: UUID, new_status: OrderStatus) -> Order:
        order = await self.repository.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        # Business rule: cancellation allowed only from PENDING and CONFIRMED
        if new_status == OrderStatus.CANCELLED:
            if order.status == OrderStatus.DELIVERED:
                raise BusinessLogicError("Cannot cancel a delivered order")
            if order.status not in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
                raise BusinessLogicError(
                    f"Cannot cancel order with status {order.status.value}. "
                    f"Cancellation is only allowed from PENDING or CONFIRMED."
                )

        order.status = new_status
        return await self.repository.update(order)

