from pydantic import BaseModel
from typing import Optional


class IncomeSourceCreate(BaseModel):
    name: str
    source_type: str = "other"


class IncomeSourceOut(BaseModel):
    id: str
    name: str
    source_type: str
    is_active: bool = True
