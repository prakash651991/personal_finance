from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client

from ..db import anon_client
from ..config import settings

bearer = HTTPBearer(auto_error=False)


def get_access_token(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return creds.credentials


def get_current_user_id(token: str = Depends(get_access_token)) -> str:
    client = anon_client()
    try:
        res = client.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = getattr(res, "user", None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return str(user.id)


def get_user_client(token: str = Depends(get_access_token)):
    from ..db import user_client as uc
    return uc(token)
