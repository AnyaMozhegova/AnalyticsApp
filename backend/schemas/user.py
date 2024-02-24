import re
from typing import Annotated

from pydantic import AfterValidator, BaseModel, EmailStr


def validate_name(name: str) -> str:
    name = name.strip()
    if len(name) == 0 or len(name) > 20:
        raise ValueError('Name must not be empty and must not exceed 20 symbols')
    return name


def validate_password(password: str) -> str:
    if not (10 <= len(password) <= 20):
        raise ValueError('Password must have a length from 10 to 20 symbols')
    pattern = (
        r'^'  # Start of string
        r'(?=.*[a-z])'  # At least one lowercase letter
        r'(?=.*[A-Z])'  # At least one uppercase letter
        r'(?=.*\d)'  # At least one digit
        r'(?=.*[@$!%*?&])'  # At least one special character from the selected set
        r'[A-Za-z\d@$!%*?&]+'  # Only allow these characters in the entire string
        r'$'  # End of string
    )

    if not re.match(pattern, password):
        raise ValueError(
            'Password must include at least one uppercase letter, '
            'one lowercase letter, one digit, and one special symbol'
        )
    return password


class UserCreate(BaseModel):
    name: Annotated[str, AfterValidator(validate_name)]
    email: EmailStr


class CustomerCreate(UserCreate):
    password: Annotated[str, AfterValidator(validate_password)]
    password_confirm: Annotated[str, AfterValidator(validate_password)]


class UserUpdate(BaseModel):
    name: Annotated[str, AfterValidator(validate_name)]
    password: Annotated[str, AfterValidator(validate_password)]
    password_confirm: Annotated[str, AfterValidator(validate_password)]


class Token(BaseModel):
    access_token: str
    id: int
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
