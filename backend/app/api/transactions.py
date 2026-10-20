from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date

from ..schemas.transactions import TransactionCreate, TransactionUpdate, TransactionOut
from ..repositories import transactions as repo
from ..security.auth import get_current_user_id, get_user_client

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=List[TransactionOut])
def list_transactions(
    user_id: str = Depends(get_current_user_id),
    client=Depends(get_user_client),
    transaction_type: Optional[str] = None,
    account_id: Optional[str] = None,
    category_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    filters = {
        "transaction_type": transaction_type,
        "account_id": account_id,
        "category_id": category_id,
        "start_date": str(start_date) if start_date else None,
        "end_date": str(end_date) if end_date else None,
    }
    rows = repo.list_transactions(client, user_id, filters)
    return [TransactionOut(**r) for r in rows]


@router.post("", response_model=TransactionOut)
def create_transaction(payload: TransactionCreate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    data = payload.model_dump(exclude_none=True)
    data["transaction_date"] = str(data["transaction_date"])
    if data.get("posting_date"):
        data["posting_date"] = str(data["posting_date"])
    row = repo.create_transaction(client, user_id, data)
    if not row:
        raise HTTPException(400, "Failed")
    return TransactionOut(**row)


@router.get("/{tx_id}", response_model=TransactionOut)
def get_transaction(tx_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.get_transaction(client, user_id, tx_id)
    if not row:
        raise HTTPException(404, "Not found")
    return TransactionOut(**row)


@router.patch("/{tx_id}", response_model=TransactionOut)
def update_transaction(tx_id: str, payload: TransactionUpdate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    data = payload.model_dump(exclude_none=True)
    if data.get("transaction_date"):
        data["transaction_date"] = str(data["transaction_date"])
    if data.get("posting_date"):
        data["posting_date"] = str(data["posting_date"])
    row = repo.update_transaction(client, user_id, tx_id, data)
    if not row:
        raise HTTPException(404, "Not found")
    return TransactionOut(**row)


@router.delete("/{tx_id}")
def delete_transaction(tx_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.delete_transaction(client, user_id, tx_id)
    if not row:
        raise HTTPException(404, "Not found")
    return {"status": "reversed"}


from pydantic import BaseModel


class TransferPayload(BaseModel):
    source_account_id: str
    destination_account_id: str
    amount: float
    transaction_date: date
    description: Optional[str] = None



