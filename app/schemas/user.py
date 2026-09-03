from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class RoleAssign(BaseModel):
    role_name: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class RoleDTO(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class UserDTO(BaseModel):
    id: UUID
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: List[RoleDTO] = []

    model_config = ConfigDict(from_attributes=True)
