from pydantic import BaseModel
from typing import Optional
from datetime import date


class AccountCreate(BaseModel):
    name: str
    institution: Optional[str] = None
    account_type: str = "bank"
    opening_balance: float = 0
    opening_balance_date: Optional[date] = None


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    institution: Optional[str] = None
    account_type: Optional[str] = None
    opening_balance: Optional[float] = None
    opening_balance_date: Optional[date] = None
    is_active: Optional[bool] = None


class AccountOut(BaseModel):
    id: str
    name: str
    institution: Optional[str] = None
    account_type: str
    opening_balance: float
    opening_balance_date: Optional[date] = None
    is_active: bool
