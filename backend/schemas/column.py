from pydantic import BaseModel


class ColumnCreate(BaseModel):
    report: int
