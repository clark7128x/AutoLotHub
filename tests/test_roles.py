import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_dealer_cannot_delete_car(dealer_client: AsyncClient):
    # DELETE /api/v1/cars/{id} requires Admin
    response = await dealer_client.delete("/api/v1/cars/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 403
    assert response.json()["detail"] == "Operation not permitted"

@pytest.mark.asyncio
async def test_dealer_cannot_decode_vin(dealer_client: AsyncClient):
    # POST /api/v1/cars/decode-vin requires Admin or Manager
    response = await dealer_client.post("/api/v1/cars/decode-vin", json={"vin": "1HGCM82633AXXXXX1"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Operation not permitted"
