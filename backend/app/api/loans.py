from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date

from ..schemas.loans import (LoanCreate, LoanUpdate, LoanOut, InstallmentOut, LoanPaymentCreate)
from ..repositories import loans as repo
from ..security.auth import get_current_user_id, get_user_client

router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("", response_model=List[LoanOut])
def list_loans(user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    return [LoanOut(**r) for r in repo.list_loans(client, user_id)]


@router.post("", response_model=LoanOut)
def create_loan(payload: LoanCreate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    data = payload.model_dump(exclude_none=True)
    for k in ("start_date", "end_date", "first_emi_date"):
        if data.get(k):
            data[k] = str(data[k])
    row = repo.create_loan(client, user_id, data)
    if not row:
        raise HTTPException(400, "Failed")
    return LoanOut(**row)


@router.get("/{loan_id}", response_model=LoanOut)
def get_loan(loan_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.get_loan(client, user_id, loan_id)
    if not row:
        raise HTTPException(404, "Not found")
    return LoanOut(**row)


@router.patch("/{loan_id}", response_model=LoanOut)
def update_loan(loan_id: str, payload: LoanUpdate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    data = payload.model_dump(exclude_none=True)
    if data.get("end_date"):
        data["end_date"] = str(data["end_date"])
    row = repo.update_loan(client, user_id, loan_id, data)
    if not row:
        raise HTTPException(404, "Not found")
    return LoanOut(**row)


@router.delete("/{loan_id}")
def archive_loan(loan_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.archive_loan(client, user_id, loan_id)
    if not row:
        raise HTTPException(404, "Not found")
    return {"status": "archived"}


@router.get("/{loan_id}/installments", response_model=List[InstallmentOut])
def list_installments(loan_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    rows = repo.list_installments(client, user_id, loan_id)
    return [InstallmentOut(**r) for r in rows]


@router.post("/{loan_id}/payments")
def record_payment(loan_id: str, payload: LoanPaymentCreate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    data = payload.model_dump(exclude_none=True)
    data["payment_date"] = str(data["payment_date"])
    return repo.record_payment(client, user_id, loan_id, data)


@router.delete("/payments/{payment_id}")
def delete_payment(payment_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    repo.delete_payment(client, user_id, payment_id)
    return {"status": "deleted"}


@router.patch("/installments/{installment_id}")
def update_installment(installment_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.update_installment(client, user_id, installment_id, payload)
    if not row:
        raise HTTPException(404, "Not found")
    return row


@router.delete("/installments/{installment_id}")
def delete_installment(installment_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    repo.delete_installment(client, user_id, installment_id)
    return {"status": "deleted"}


@router.post("/{loan_id}/reschedule-preview")
def reschedule_preview(loan_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    return repo.reschedule_preview(client, user_id, loan_id, payload.get("end_date"), payload.get("emi_amount"))


@router.post("/{loan_id}/reschedule")
def reschedule(loan_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    return repo.reschedule_confirm(client, user_id, loan_id, payload.get("end_date"), payload.get("emi_amount"))
