from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order
from typing import List, Optional

class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, dealer_id: Optional[UUID] = None) -> List[Order]:
        stmt = select(Order)
        if dealer_id:
            # Data Scoping: if dealer_id is provided, limit to their orders
            stmt = stmt.where(Order.dealer_id == dealer_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_by_id(self, order_id: UUID, dealer_id: Optional[UUID] = None) -> Optional[Order]:
        stmt = select(Order).where(Order.id == order_id)
        if dealer_id:
            stmt = stmt.where(Order.dealer_id == dealer_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, order: Order) -> Order:
        self.session.add(order)
        await self.session.flush()
        await self.session.refresh(order)
        return order

    async def update(self, order: Order) -> Order:
        await self.session.flush()
        await self.session.refresh(order)
        return order
