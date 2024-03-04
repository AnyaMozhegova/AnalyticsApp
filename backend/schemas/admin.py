from schemas.user import UserCreate, UserUpdate


class AdminCreate(UserCreate):
    parent_admin: int


class AdminUpdate(UserUpdate):
    pass
