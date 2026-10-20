from pydantic import BaseModel
from typing import Optional
from datetime import date


class TransactionCreate(BaseModel):
    account_id: Optional[str] = None
    card_id: Optional[str] = None
    transaction_type: str
    amount: float
    currency: str = "INR"
    transaction_date: date
    posting_date: Optional[date] = None
    category_id: Optional[str] = None
    income_source_id: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    transfer_group_id: Optional[str] = None
    linked_transaction_id: Optional[str] = None
    recurring_occurrence_id: Optional[str] = None
    status: str = "posted"


class TransactionUpdate(BaseModel):
    account_id: Optional[str] = None
    transaction_type: Optional[str] = None
    amount: Optional[float] = None
    transaction_date: Optional[date] = None
    posting_date: Optional[date] = None
    category_id: Optional[str] = None
    income_source_id: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class TransactionOut(BaseModel):
    id: str
    user_id: str
    account_id: Optional[str] = None
    transaction_type: str
    amount: float
    currency: str = "INR"
    transaction_date: date
    posting_date: Optional[date] = None
    category_id: Optional[str] = None
    income_source_id: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    transfer_group_id: Optional[str] = None
    linked_transaction_id: Optional[str] = None
    status: str = "posted"
