from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..schemas.savings_goals import SavingsGoalCreate, SavingsGoalOut, GoalEventCreate
from ..repositories import savings_goals as repo
from ..security.auth import get_current_user_id, get_user_client

router = APIRouter(prefix="/savings-goals", tags=["savings-goals"])


@router.get("", response_model=List[SavingsGoalOut])
def list_goals(user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    return [SavingsGoalOut(**r) for r in repo.list_goals(client, user_id)]


@router.post("", response_model=SavingsGoalOut)
def create_goal(payload: SavingsGoalCreate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.create_goal(client, user_id, payload.model_dump(exclude_none=True))
    if not row:
        raise HTTPException(400, "Failed")
    return SavingsGoalOut(**row)


@router.patch("/{goal_id}", response_model=SavingsGoalOut)
def update_goal(goal_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    data = {k: v for k, v in payload.items() if v is not None}
    for k in ("start_date", "target_date"):
        if data.get(k):
            data[k] = str(data[k])
    row = repo.update_goal(client, user_id, goal_id, data)
    if not row:
        raise HTTPException(404, "Not found")
    return SavingsGoalOut(**row)


@router.delete("/{goal_id}")
def delete_goal(goal_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    repo.delete_goal(client, user_id, goal_id)
    return {"status": "deleted"}


@router.patch("/events/{event_id}")
def update_event(event_id: str, payload: dict, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    row = repo.update_event(client, user_id, event_id, payload)
    if not row:
        raise HTTPException(404, "Not found")
    return row


@router.delete("/events/{event_id}")
def delete_event(event_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    repo.delete_event(client, user_id, event_id)
    return {"status": "deleted"}


@router.get("/{goal_id}")
def get_goal(goal_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    return repo.get_goal_balance(client, user_id, goal_id)


@router.post("/{goal_id}/events")
def add_event(goal_id: str, payload: GoalEventCreate, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    data = payload.model_dump(exclude_none=True)
    data["goal_id"] = goal_id
    data["event_date"] = str(data["event_date"])
    return repo.add_event(client, user_id, data)


@router.get("/{goal_id}/events")
def list_events(goal_id: str, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    return repo.list_events(client, user_id, goal_id)
