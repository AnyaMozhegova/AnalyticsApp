from pydantic import BaseModel
from schemas.user import UserCreate, UserUpdate


class AdminCreate(UserCreate):
    parent_admin: int


class AdminDelete(BaseModel):
    admin_to_delete: int


class AdminUpdate(UserUpdate):
    pass
