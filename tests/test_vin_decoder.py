import pytest
from app.external_services.vin_decoder import vin_decoder_service
from app.external_services.exceptions import ExternalServiceError

@pytest.mark.asyncio
async def test_decode_vin_success_clean():
    result = await vin_decoder_service.decode_vin("1HGCM82633AXXXXX1")
    assert result.history_status == "CLEAN"
    assert result.make == "Honda"

@pytest.mark.asyncio
async def test_decode_vin_invalid_length():
    with pytest.raises(ExternalServiceError) as exc_info:
        await vin_decoder_service.decode_vin("SHORTVIN123")
    assert exc_info.value.status_code == 400
    assert exc_info.value.code == "INVALID_VIN"

@pytest.mark.asyncio
async def test_decode_vin_not_found():
    with pytest.raises(ExternalServiceError) as exc_info:
        await vin_decoder_service.decode_vin("1HGCM82633AXXXXXX") # Valid length, but not in mock DB
    assert exc_info.value.status_code == 404
    assert exc_info.value.code == "VIN_NOT_FOUND"
