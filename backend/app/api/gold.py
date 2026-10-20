from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..schemas.gold import GoldHoldingCreate, GoldHoldingOut
from ..repositories import gold as repo
from ..security.auth import get_current_user_id, get_user_client

router = APIRouter(prefix="/gold", tags=["gold"])


@router.get("", response_model=List[GoldHoldingOut])
def list_gold(user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    return [GoldHoldingOut(**r) for r in repo.list_gold(client, user_id)]


@router.post("", response_model=GoldHoldingOut)
def create_gold(payload: GoldHoldingCreate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.create_gold(client, user_id, payload.model_dump(exclude_none=True))
    if not row:
        raise HTTPException(400, "Failed")
    return GoldHoldingOut(**row)


@router.patch("/{gold_id}", response_model=GoldHoldingOut)
def update_gold(gold_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    data = {k: v for k, v in payload.items() if v is not None}
    if data.get("purchase_date"):
        data["purchase_date"] = str(data["purchase_date"])
    row = repo.update_gold(client, user_id, gold_id, data)
    if not row:
        raise HTTPException(404, "Not found")
    return GoldHoldingOut(**row)


@router.delete("/{gold_id}")
def delete_gold(gold_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    repo.delete_gold(client, user_id, gold_id)
    return {"status": "deleted"}
