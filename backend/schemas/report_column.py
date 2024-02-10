from typing import Annotated, List, Optional

from pydantic import AfterValidator, BaseModel


def validate_name(name: str) -> str:
    name = name.strip()
    if len(name) == 0 or len(name) > 20:
        raise ValueError('Name must not be empty and must not exceed 20 symbols')
    return name


class ReportColumnCreate(BaseModel):
    name: Annotated[str, AfterValidator(validate_name)]
    column_data: List[Optional[float]]
    indicator_values: Optional[List[int]] = None


class ReportColumnUpdate(BaseModel):
    indicator_values: List[int]
