from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date

from ..schemas.credit_cards import (CreditCardCreate, CreditCardOut, CCStatementOut, CCTransactionCreate, CCPaymentCreate)
from ..repositories import credit_cards as repo
from ..security.auth import get_current_user_id, get_user_client

router = APIRouter(prefix="/credit-cards", tags=["credit-cards"])


@router.get("", response_model=List[CreditCardOut])
def list_cards(user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    return [CreditCardOut(**r) for r in repo.list_cards(client, user_id)]


@router.post("", response_model=CreditCardOut)
def create_card(payload: CreditCardCreate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.create_card(client, user_id, payload.model_dump(exclude_none=True))
    if not row:
        raise HTTPException(400, "Failed")
    return CreditCardOut(**row)


@router.patch("/{card_id}", response_model=CreditCardOut)
def update_card(card_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.update_card(client, user_id, card_id, {k: v for k, v in payload.items() if v is not None})
    if not row:
        raise HTTPException(404, "Not found")
    return CreditCardOut(**row)


@router.delete("/{card_id}")
def delete_card(card_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    repo.delete_card(client, user_id, card_id)
    return {"status": "deleted"}


@router.patch("/statements/{statement_id}", response_model=CCStatementOut)
def update_statement(statement_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.update_statement(client, user_id, statement_id, payload)
    if not row:
        raise HTTPException(404, "Not found")
    return CCStatementOut(**row)


@router.delete("/statements/{statement_id}")
def delete_statement(statement_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    repo.delete_statement(client, user_id, statement_id)
    return {"status": "deleted"}


@router.patch("/transactions/{cc_tx_id}")
def update_cc_transaction(cc_tx_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.update_cc_transaction(client, user_id, cc_tx_id, payload)
    if not row:
        raise HTTPException(404, "Not found")
    return row


@router.delete("/transactions/{cc_tx_id}")
def delete_cc_transaction(cc_tx_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    repo.delete_cc_transaction(client, user_id, cc_tx_id)
    return {"status": "deleted"}


@router.delete("/payments/{payment_id}")
def delete_payment(payment_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    repo.delete_payment(client, user_id, payment_id)
    return {"status": "deleted"}


@router.get("/{card_id}/statements", response_model=List[CCStatementOut])
def list_statements(card_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    rows = repo.list_statements(client, user_id, card_id)
    return [CCStatementOut(**r) for r in rows]


@router.post("/{card_id}/statements", response_model=CCStatementOut)
def create_statement(card_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    data = dict(payload)
    data["card_id"] = card_id
    if data.get("period_start"):
        data["period_start"] = str(data["period_start"])
    if data.get("period_end"):
        data["period_end"] = str(data["period_end"])
    if data.get("statement_date"):
        data["statement_date"] = str(data["statement_date"])
    if data.get("due_date"):
        data["due_date"] = str(data["due_date"])
    row = repo.create_statement(client, user_id, data)
    if not row:
        raise HTTPException(400, "Failed")
    return CCStatementOut(**row)


@router.get("/{card_id}/unbilled")
def list_unbilled(card_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    return repo.list_unbilled(client, user_id, card_id)


@router.post("/{card_id}/transactions")
def create_cc_transaction(card_id: str, payload: CCTransactionCreate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    data = payload.model_dump(exclude_none=True)
    data["card_id"] = card_id
    data["purchase_date"] = str(data["purchase_date"])
    if data.get("posting_date"):
        data["posting_date"] = str(data["posting_date"])
    row = repo.create_cc_transaction(client, user_id, data)
    if not row:
        raise HTTPException(400, "Failed")
    return row


@router.post("/{card_id}/payments")
def record_payment(card_id: str, payload: CCPaymentCreate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    data = payload.model_dump(exclude_none=True)
    data["card_id"] = card_id
    data["payment_date"] = str(data["payment_date"])
    return repo.record_payment(client, user_id, data)
