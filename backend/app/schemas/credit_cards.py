from pydantic import BaseModel
from typing import Optional
from datetime import date


class CreditCardCreate(BaseModel):
    nickname: str
    issuer: Optional[str] = None
    last4: Optional[str] = None
    credit_limit: Optional[float] = None
    statement_day: Optional[int] = None
    due_day: Optional[int] = None
    cycle_rule: str = "standard"


class CreditCardOut(BaseModel):
    id: str
    nickname: str
    issuer: Optional[str] = None
    last4: Optional[str] = None
    credit_limit: Optional[float] = None
    statement_day: Optional[int] = None
    due_day: Optional[int] = None
    cycle_rule: str = "standard"
    is_active: bool = True


class CCStatementOut(BaseModel):
    id: str
    card_id: str
    period_start: date
    period_end: date
    statement_date: Optional[date] = None
    status: str
    statement_total: float
    minimum_due: Optional[float] = None
    due_date: Optional[date] = None
    paid_amount: float = 0


class CCTransactionCreate(BaseModel):
    card_id: str
    kind: str = "purchase"
    purchase_date: date
    posting_date: Optional[date] = None
    amount: float
    description: Optional[str] = None
    issuer_ref: Optional[str] = None
    statement_id: Optional[str] = None


class CCPaymentCreate(BaseModel):
    card_id: str
    amount: float
    payment_date: date
    account_id: Optional[str] = None
    statement_id: Optional[str] = None
    description: Optional[str] = None
