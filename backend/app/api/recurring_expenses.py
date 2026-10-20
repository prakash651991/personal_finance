from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..schemas.recurring_expenses import RecurringExpenseCreate, RecurringExpenseOut
from ..repositories import recurring_expenses as repo
from ..security.auth import get_current_user_id, get_user_client

router = APIRouter(prefix="/recurring-expenses", tags=["recurring-expenses"])


@router.get("", response_model=List[RecurringExpenseOut])
def list_recurring(user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    return [RecurringExpenseOut(**r) for r in repo.list_recurring(client, user_id)]


@router.post("", response_model=RecurringExpenseOut)
def create_recurring(payload: RecurringExpenseCreate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    data = payload.model_dump(exclude_none=True)
    for k in ("first_due_date", "end_date"):
        if data.get(k):
            data[k] = str(data[k])
    row = repo.create_recurring(client, user_id, data)
    if not row:
        raise HTTPException(400, "Failed")
    return RecurringExpenseOut(**row)


@router.patch("/{recurring_id}", response_model=RecurringExpenseOut)
def update_recurring(recurring_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    data = {k: v for k, v in payload.items() if v is not None}
    for k in ("first_due_date", "end_date"):
        if data.get(k):
            data[k] = str(data[k])
    row = repo.update_recurring(client, user_id, recurring_id, data)
    if not row:
        raise HTTPException(404, "Not found")
    return RecurringExpenseOut(**row)


@router.delete("/{recurring_id}")
def delete_recurring(recurring_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    repo.delete_recurring(client, user_id, recurring_id)
    return {"status": "deleted"}


@router.get("/occurrences")
def list_occurrences(user_id: str = Depends(get_current_user_id), client=Depends(get_user_client), recurring_id: str | None = None):
    return repo.list_occurrences(client, user_id, recurring_id)


@router.patch("/occurrences/{occurrence_id}")
def update_occurrence(occurrence_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.update_occurrence(client, user_id, occurrence_id, payload)
    if not row:
        raise HTTPException(404, "Not found")
    return row


@router.delete("/occurrences/{occurrence_id}")
def delete_occurrence(occurrence_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    repo.delete_occurrence(client, user_id, occurrence_id)
    return {"status": "deleted"}
