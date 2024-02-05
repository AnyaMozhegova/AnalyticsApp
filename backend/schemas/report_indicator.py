from typing import Annotated

from pydantic import AfterValidator, BaseModel


def validate_name(name: str) -> str:
    name = name.strip()
    if len(name) == 0 or len(name) > 20:
        raise ValueError('Name must not be empty and must not exceed 20 symbols')
    return name


class ReportIndicatorCreate(BaseModel):
    name: Annotated[str, AfterValidator(validate_name)]


class ReportIndicatorUpdate(BaseModel):
    name: Annotated[str, AfterValidator(validate_name)]
