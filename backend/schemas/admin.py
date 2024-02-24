from typing import Annotated, Optional

from pydantic import AfterValidator, BaseModel
from schemas.user import UserCreate, validate_name, validate_password


class AdminCreate(UserCreate):
    parent_admin: int


class AdminDelete(BaseModel):
    admin_to_delete: int


class AdminUpdate(BaseModel):
    name: Optional[Annotated[str, AfterValidator(validate_name)]] = None
    password: Optional[Annotated[str, AfterValidator(validate_password)]] = None
    password_confirm: Optional[Annotated[str, AfterValidator(validate_password)]] = None
