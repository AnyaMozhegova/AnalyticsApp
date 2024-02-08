from pydantic import BaseModel


class IndicatorValueCreate(BaseModel):
    report_indicator: int
    column: int
