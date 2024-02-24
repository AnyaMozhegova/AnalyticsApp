from typing import Annotated

from pydantic import AfterValidator
from schemas.user import UserCreate, UserUpdate, validate_password


class CustomerCreate(UserCreate):
    password: Annotated[str, AfterValidator(validate_password)]
    password_confirm: Annotated[str, AfterValidator(validate_password)]


class CustomerUpdate(UserUpdate):
    pass
