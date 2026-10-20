from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..schemas.accounts import AccountCreate, AccountUpdate, AccountOut
from ..repositories import accounts as repo
from ..security.auth import get_current_user_id, get_user_client

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=List[AccountOut])
def list_accounts(user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    rows = repo.list_accounts(client, user_id)
    return [AccountOut(**r) for r in rows]


@router.post("", response_model=AccountOut)
def create_account(payload: AccountCreate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.create_account(client, user_id, payload.model_dump(exclude_none=True))
    if not row:
        raise HTTPException(400, "Failed to create account")
    return AccountOut(**row)


@router.patch("/{account_id}", response_model=AccountOut)
def update_account(account_id: str, payload: AccountUpdate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.update_account(client, user_id, account_id, payload.model_dump(exclude_none=True))
    if not row:
        raise HTTPException(404, "Account not found")
    return AccountOut(**row)


@router.delete("/{account_id}")
def delete_account(account_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.archive_account(client, user_id, account_id)
    if not row:
        raise HTTPException(404, "Account not found")
    return {"status": "archived"}
