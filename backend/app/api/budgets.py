from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..schemas.budgets import BudgetCreate, BudgetOut
from ..repositories import budgets as repo
from ..security.auth import get_current_user_id, get_user_client

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=List[BudgetOut])
def list_budgets(user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    return [BudgetOut(**r) for r in repo.list_budgets(client, user_id)]


@router.post("", response_model=BudgetOut)
def create_budget(payload: BudgetCreate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.create_budget(client, user_id, payload.model_dump(exclude_none=True))
    if not row:
        raise HTTPException(400, "Failed")
    return BudgetOut(**row)


@router.patch("/{budget_id}", response_model=BudgetOut)
def update_budget(budget_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.update_budget(client, user_id, budget_id, {k: v for k, v in payload.items() if v is not None})
    if not row:
        raise HTTPException(404, "Not found")
    return BudgetOut(**row)


@router.delete("/{budget_id}")
def delete_budget(budget_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    repo.delete_budget(client, user_id, budget_id)
    return {"status": "deleted"}
