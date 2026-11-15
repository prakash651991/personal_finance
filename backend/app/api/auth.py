import json
import urllib.request
import urllib.error
from fastapi import APIRouter, HTTPException
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


def _post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        settings.SUPABASE_URL + path,
        data=data,
        headers={"apikey": settings.SUPABASE_ANON_KEY, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            j = json.loads(raw)
        except Exception:
            j = {"msg": raw}
        raise HTTPException(status_code=e.code, detail=j.get("msg") or j.get("error_description") or raw)
    except urllib.error.URLError:
        raise HTTPException(
            status_code=503,
            detail="Identity service unreachable. The Supabase project may be deleted or paused.",
        )


@router.post("/login")
def login(payload: dict):
    return _post("/auth/v1/token?grant_type=password", {"email": payload.get("email"), "password": payload.get("password")})


@router.post("/signup")
def signup(payload: dict):
    return _post("/auth/v1/signup", {"email": payload.get("email"), "password": payload.get("password")})
