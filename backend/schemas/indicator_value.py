from pydantic import BaseModel


class IndicatorValueCreate(BaseModel):
    reportIndicator: int
    value: float
