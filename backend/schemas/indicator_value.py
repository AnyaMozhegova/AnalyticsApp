from pydantic import BaseModel


class IndicatorValueCreate(BaseModel):
    report_indicator: int
    column: int


class IndicatorValueGetBase(BaseModel):
    user: int
    report: int
    column: int


class IndicatorValuesGet(IndicatorValueGetBase):
    pass


class IndicatorValueGet(IndicatorValueGetBase):
    indicator_value: int


class IndicatorValueGetByName(IndicatorValueGetBase):
    report_indicator_name: str
