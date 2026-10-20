from pydantic import BaseModel
from typing import Optional
from datetime import date


class SavingsGoalCreate(BaseModel):
    name: str
    goal_type: str = "general"
    target_amount: float
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    starting_balance: float = 0
    linked_account_id: Optional[str] = None
    notes: Optional[str] = None


class SavingsGoalOut(BaseModel):
    id: str
    name: str
    goal_type: str = "general"
    target_amount: float
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    starting_balance: float = 0
    linked_account_id: Optional[str] = None
    status: str = "active"
    notes: Optional[str] = None


class GoalEventCreate(BaseModel):
    goal_id: Optional[str] = None
    event_type: str = "contribution"
    amount: float
    event_date: date
    account_id: Optional[str] = None
    notes: Optional[str] = None
