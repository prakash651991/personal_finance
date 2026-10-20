from fastapi import APIRouter, Depends, HTTPException

from ..schemas.profile import ProfileOut, ProfileUpdate
from ..repositories import profile as repo
from ..security.auth import get_current_user_id, get_user_client

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
def get_profile(user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.get_profile(client, user_id)
    if not row:
        raise HTTPException(404, "Not found")
    return ProfileOut(**row)


@router.patch("", response_model=ProfileOut)
def update_profile(payload: ProfileUpdate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.update_profile(client, user_id, payload.model_dump(exclude_none=True))
    if not row:
        raise HTTPException(404, "Not found")
    return ProfileOut(**row)
