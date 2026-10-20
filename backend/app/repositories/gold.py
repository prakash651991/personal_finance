from supabase import Client


def list_gold(client: Client, user_id: str):
    res = client.table("gold_holdings").select("*").eq("user_id", user_id).order("purchase_date", desc=True).execute()
    return res.data or []


def create_gold(client: Client, user_id: str, payload: dict):
    payload["user_id"] = user_id
    if payload.get("purchase_date"):
        payload["purchase_date"] = str(payload["purchase_date"])
    res = client.table("gold_holdings").insert(payload).execute()
    return (res.data or [None])[0]


def update_gold(client: Client, user_id: str, gold_id: str, payload: dict):
    if payload.get("purchase_date"):
        payload["purchase_date"] = str(payload["purchase_date"])
    res = client.table("gold_holdings").update(payload).eq("user_id", user_id).eq("id", gold_id).execute()
    data = res.data or []
    return data[0] if data else None


def delete_gold(client: Client, user_id: str, gold_id: str):
    client.table("gold_holdings").delete().eq("user_id", user_id).eq("id", gold_id).execute()
    return True
