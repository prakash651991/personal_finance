from pydantic import BaseModel
from typing import Optional
from datetime import date


class LoanCreate(BaseModel):
    name: str
    lender_name: Optional[str] = None
    loan_type: str = "personal"
    start_date: date
    end_date: date
    first_emi_date: Optional[date] = None
    emi_due_day: Optional[int] = None
    emi_amount: float
    original_principal: Optional[float] = None
    annual_interest_rate: Optional[float] = None
    interest_type: Optional[str] = None
    payment_account_id: Optional[str] = None
    notes: Optional[str] = None


class LoanUpdate(BaseModel):
    name: Optional[str] = None
    lender_name: Optional[str] = None
    end_date: Optional[date] = None
    emi_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class LoanOut(BaseModel):
    id: str
    name: str
    lender_name: Optional[str] = None
    loan_type: str = "personal"
    start_date: date
    end_date: date
    first_emi_date: Optional[date] = None
    emi_due_day: Optional[int] = None
    emi_amount: float
    original_principal: Optional[float] = None
    annual_interest_rate: Optional[float] = None
    interest_type: Optional[str] = None
    payment_account_id: Optional[str] = None
    status: str = "active"
    notes: Optional[str] = None


class InstallmentOut(BaseModel):
    id: str
    loan_id: str
    installment_number: int
    due_date: date
    expected_amount: float
    paid_amount: float = 0
    status: str = "upcoming"
    principal_component: Optional[float] = None
    interest_component: Optional[float] = None


class LoanPaymentCreate(BaseModel):
    amount: float
    payment_date: date
    installment_id: Optional[str] = None
    account_id: Optional[str] = None
    notes: Optional[str] = None
