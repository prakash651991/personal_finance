from pydantic import BaseModel
from typing import Optional
from datetime import date


class BudgetCreate(BaseModel):
    category_id: Optional[str] = None
    amount: float
    period_type: str = "monthly"
    period_start: date
    period_end: date
    rollover: bool = False
    alert_threshold: float = 80


class BudgetOut(BaseModel):
    id: str
    category_id: Optional[str] = None
    amount: float
    period_type: str = "monthly"
    period_start: date
    period_end: date
    rollover: bool = False
    alert_threshold: float = 80
    is_active: bool = True
