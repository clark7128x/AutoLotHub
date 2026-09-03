from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.schemas.user import UserDTO
from app.models.user import User
from app.api.dependencies.auth import get_current_user, require_role
from app.core.database import get_db

router = APIRouter()

@router.get("/me", response_model=UserDTO)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("", response_model=List[UserDTO])
async def read_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Manager"]))
):
    result = await db.execute(select(User))
    return list(result.scalars().all())
