from pydantic import BaseModel
from typing import Optional


class ProfileOut(BaseModel):
    id: Optional[str] = None
    display_name: Optional[str] = None
    default_currency: str = "INR"
    timezone: str = "Asia/Kolkata"
    budget_period_start_day: int = 1
    notification_prefs: dict = {}


class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    default_currency: Optional[str] = None
    timezone: Optional[str] = None
    budget_period_start_day: Optional[int] = None
    notification_prefs: Optional[dict] = None
