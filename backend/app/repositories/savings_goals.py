from supabase import Client


def list_goals(client: Client, user_id: str):
    res = client.table("savings_goals").select("*").eq("user_id", user_id).execute()
    return res.data or []


def create_goal(client: Client, user_id: str, payload: dict):
    payload["user_id"] = user_id
    for k in ("start_date", "target_date"):
        if payload.get(k):
            payload[k] = str(payload[k])
    res = client.table("savings_goals").insert(payload).execute()
    return (res.data or [None])[0]


def update_goal(client: Client, user_id: str, goal_id: str, payload: dict):
    for k in ("start_date", "target_date"):
        if payload.get(k):
            payload[k] = str(payload[k])
    res = client.table("savings_goals").update(payload).eq("user_id", user_id).eq("id", goal_id).execute()
    data = res.data or []
    return data[0] if data else None


def delete_goal(client: Client, user_id: str, goal_id: str):
    client.table("goal_events").delete().eq("user_id", user_id).eq("goal_id", goal_id).execute()
    client.table("savings_goals").delete().eq("user_id", user_id).eq("id", goal_id).execute()
    return True


def update_event(client: Client, user_id: str, event_id: str, payload: dict):
    if payload.get("event_date"):
        payload["event_date"] = str(payload["event_date"])
    res = client.table("goal_events").update(payload).eq("user_id", user_id).eq("id", event_id).execute()
    data = res.data or []
    return data[0] if data else None


def delete_event(client: Client, user_id: str, event_id: str):
    client.table("goal_events").delete().eq("user_id", user_id).eq("id", event_id).execute()
    return True


def get_goal_balance(client: Client, user_id: str, goal_id: str):
    goal = client.table("savings_goals").select("*").eq("user_id", user_id).eq("id", goal_id).limit(1).execute()
    g = (goal.data or [None])[0]
    if not g:
        return None
    events = client.table("goal_events").select("*").eq("user_id", user_id).eq("goal_id", goal_id).execute().data or []
    balance = float(g.get("starting_balance") or 0)
    for e in events:
        amt = float(e.get("amount") or 0)
        if e["event_type"] == "contribution":
            balance += amt
        elif e["event_type"] == "withdrawal":
            balance -= amt
        else:
            balance += amt
    return {"goal": g, "balance": balance, "events": events}


def add_event(client: Client, user_id: str, payload: dict):
    payload["user_id"] = user_id
    if payload.get("event_date"):
        payload["event_date"] = str(payload["event_date"])
    res = client.table("goal_events").insert(payload).execute()
    return (res.data or [None])[0]


def list_events(client: Client, user_id: str, goal_id: str):
    res = client.table("goal_events").select("*").eq("user_id", user_id).eq("goal_id", goal_id).order("event_date", desc=True).execute()
    return res.data or []
