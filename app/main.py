from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.v1 import auth, users, cars, orders
from app.external_services.exceptions import ExternalServiceError
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(cars.router, prefix="/api/v1/cars", tags=["cars"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])

@app.exception_handler(ExternalServiceError)
async def external_service_error_handler(request: Request, exc: ExternalServiceError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )
