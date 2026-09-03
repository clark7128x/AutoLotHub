import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.models.user import User, Role
from app.models.order import Order, OrderStatus

@pytest.mark.asyncio
async def test_dealer_cannot_see_other_dealer_orders():
    """
    Data Scoping: Dealer A must NOT see orders belonging to Dealer B.
    GET /orders for a Dealer should return only their own orders.
    """
    dealer_a_id = uuid4()
    dealer_b_id = uuid4()
    now = datetime.utcnow()

    dealer_a = User(id=dealer_a_id, email="dealer_a@test.com", is_active=True)
    dealer_a.roles = [Role(name="Dealer")]

    # Orders: one for dealer A, one for dealer B
    order_a = Order(
        id=uuid4(),
        car_lot_id=uuid4(),
        dealer_id=dealer_a_id,
        status=OrderStatus.PENDING,
        notes="Order for dealer A",
        created_at=now,
        updated_at=now,
    )
    order_b = Order(
        id=uuid4(),
        car_lot_id=uuid4(),
        dealer_id=dealer_b_id,
        status=OrderStatus.PENDING,
        notes="Order for dealer B",
        created_at=now,
        updated_at=now,
    )

    mock_db = AsyncMock()

    # Mock the repository's get_all to simulate data scoping:
    # When dealer_id is provided, return only that dealer's orders
    async def mock_get_all(dealer_id=None):
        all_orders = [order_a, order_b]
        if dealer_id:
            return [o for o in all_orders if o.dealer_id == dealer_id]
        return all_orders

    app.dependency_overrides[get_current_user] = lambda: dealer_a
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.api.v1.orders.OrderRepository") as MockRepo:
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.get_all = mock_get_all

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/orders")

    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    orders = response.json()

    # Dealer A should see only their own order
    assert len(orders) == 1
    assert orders[0]["dealer_id"] == str(dealer_a_id)
    assert orders[0]["notes"] == "Order for dealer A"

    # Dealer A must NOT see dealer B's order
    dealer_b_order_ids = [o["id"] for o in orders if o["dealer_id"] == str(dealer_b_id)]
    assert len(dealer_b_order_ids) == 0, "Dealer A must not see Dealer B's orders"
