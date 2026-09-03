from app.repositories.user import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate
from typing import Optional

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
        
    async def create_dealer(self, user_data: UserCreate, hashed_password: str) -> User:
        existing = await self.repository.get_by_email(user_data.email)
        if existing:
            raise ValueError("User with this email already exists")
            
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        dealer_role = await self.repository.get_role_by_name("Dealer")
        if dealer_role:
            new_user.roles.append(dealer_role)
            
        return await self.repository.create(new_user)
        
    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.repository.get_by_email(email)
