from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.config import settings
from app.schemas.user import UserCreate, UserDTO
from app.schemas.token import Token
from app.services.user import UserService
from app.repositories.user import UserRepository

router = APIRouter()

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
async def register_dealer(
    user_in: UserCreate, db: AsyncSession = Depends(get_db)
):
    """
    Відкрита реєстрація нового Дилера (користувач автоматично отримує роль `Dealer`).
    Адміни та Менеджери створюються виключно через внутрішню панель (суперюзером).
    """
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    
    hashed_password = get_password_hash(user_in.password)
    try:
        user = await user_service.create_dealer(user_in, hashed_password)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    
    user = await user_service.get_by_email(email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(subject=user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    body: RefreshRequest, db: AsyncSession = Depends(get_db)
):
    """
    Оновлення access_token за допомогою дійсного refresh_token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            body.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_type: str = payload.get("type")
        user_id_str: str = payload.get("sub")
        if token_type != "refresh" or user_id_str is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id_str)
    if user is None or not user.is_active:
        raise credentials_exception

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(subject=user.id)
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }
