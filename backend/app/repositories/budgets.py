from supabase import Client


def list_budgets(client: Client, user_id: str):
    res = client.table("budgets").select("*").eq("user_id", user_id).execute()
    return res.data or []


def create_budget(client: Client, user_id: str, payload: dict):
    payload["user_id"] = user_id
    for k in ("period_start", "period_end"):
        if payload.get(k):
            payload[k] = str(payload[k])
    res = client.table("budgets").insert(payload).execute()
    return (res.data or [None])[0]


def update_budget(client: Client, user_id: str, budget_id: str, payload: dict):
    for k in ("period_start", "period_end"):
        if payload.get(k):
            payload[k] = str(payload[k])
    res = client.table("budgets").update(payload).eq("user_id", user_id).eq("id", budget_id).execute()
    data = res.data or []
    return data[0] if data else None


def delete_budget(client: Client, user_id: str, budget_id: str):
    client.table("budgets").delete().eq("user_id", user_id).eq("id", budget_id).execute()
    return True
