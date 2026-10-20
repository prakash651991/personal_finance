from pydantic import BaseModel
from typing import Optional
from datetime import date


class RecurringExpenseCreate(BaseModel):
    name: str
    category_id: Optional[str] = None
    expected_amount: float
    frequency: str = "monthly"
    first_due_date: date
    end_date: Optional[date] = None
    payment_account_id: Optional[str] = None


class RecurringExpenseOut(BaseModel):
    id: str
    name: str
    category_id: Optional[str] = None
    expected_amount: float
    frequency: str = "monthly"
    first_due_date: date
    end_date: Optional[date] = None
    payment_account_id: Optional[str] = None
    status: str = "active"
