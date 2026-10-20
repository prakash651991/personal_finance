from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..schemas.categories import CategoryCreate, CategoryOut
from ..repositories import categories as repo
from ..security.auth import get_current_user_id, get_user_client

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[CategoryOut])
def list_categories(user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    return [CategoryOut(**r) for r in repo.list_categories(client, user_id)]


@router.post("", response_model=CategoryOut)
def create_category(payload: CategoryCreate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.create_category(client, user_id, payload.model_dump(exclude_none=True))
    if not row:
        raise HTTPException(400, "Failed")
    return CategoryOut(**row)


@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(category_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.update_category(client, user_id, category_id, {k: v for k, v in payload.items() if v is not None})
    if not row:
        raise HTTPException(404, "Not found")
    return CategoryOut(**row)


@router.delete("/{category_id}")
def delete_category(category_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    repo.delete_category(client, user_id, category_id)
    return {"status": "deleted"}
