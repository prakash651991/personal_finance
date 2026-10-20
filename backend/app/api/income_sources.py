from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..schemas.income_sources import IncomeSourceCreate, IncomeSourceOut
from ..repositories import income_sources as repo
from ..security.auth import get_current_user_id, get_user_client

router = APIRouter(prefix="/income-sources", tags=["income-sources"])


@router.get("", response_model=List[IncomeSourceOut])
def list_income_sources(user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    return [IncomeSourceOut(**r) for r in repo.list_income_sources(client, user_id)]


@router.post("", response_model=IncomeSourceOut)
def create_income_source(payload: IncomeSourceCreate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.create_income_source(client, user_id, payload.model_dump(exclude_none=True))
    if not row:
        raise HTTPException(400, "Failed")
    return IncomeSourceOut(**row)


@router.patch("/{source_id}", response_model=IncomeSourceOut)
def update_income_source(source_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.update_income_source(client, user_id, source_id, {k: v for k, v in payload.items() if v is not None})
    if not row:
        raise HTTPException(404, "Not found")
    return IncomeSourceOut(**row)


@router.delete("/{source_id}")
def delete_income_source(source_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    repo.delete_income_source(client, user_id, source_id)
    return {"status": "deleted"}
