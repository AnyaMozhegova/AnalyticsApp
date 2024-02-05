from pydantic import BaseModel


class ReportCreate(BaseModel):
    user: int
