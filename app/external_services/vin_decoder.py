import asyncio
from app.schemas.car_lot import ExternalCarDataDTO
from app.external_services.exceptions import ExternalServiceError

class MockVINDecoderService:
    async def decode_vin(self, vin: str) -> ExternalCarDataDTO:
        # Simulate network latency
        await asyncio.sleep(2)
        
        vin = vin.upper()
        
        # Validation: 17 chars, no I, O, Q
        if len(vin) != 17 or any(c in vin for c in ['I', 'O', 'Q']):
            raise ExternalServiceError(
                code="INVALID_VIN",
                message="Введено некоректний VIN код. Довжина має бути 17 символів, без літер I, O, Q.",
                status_code=400
            )
            
        if vin == "1HGCM82633AXXXXX1":
            return ExternalCarDataDTO(
                vin=vin,
                make="Honda",
                model="Accord",
                year=2018,
                country="Japan",
                history_status="CLEAN",
                engine="2.4L I4",
                damage=None
            )
            
        if vin == "5YJ3E1EA3JXXXXXX2":
            return ExternalCarDataDTO(
                vin=vin,
                make="Tesla",
                model="Model 3",
                year=2020,
                country="USA",
                history_status="SALVAGE_AUCTION",
                damage="Front End",
                engine="Electric"
            )
            
        # If not found
        raise ExternalServiceError(
            code="VIN_NOT_FOUND",
            message="Дані по автомобілю з таким VIN не знайдено в реєстрах.",
            status_code=404
        )

# Instantiate a singleton to be used across the app
vin_decoder_service = MockVINDecoderService()
