from supabase import Client


def list_income_sources(client: Client, user_id: str):
    res = client.table("income_sources").select("*").eq("user_id", user_id).execute()
    return res.data or []


def create_income_source(client: Client, user_id: str, payload: dict):
    payload["user_id"] = user_id
    res = client.table("income_sources").insert(payload).execute()
    return (res.data or [None])[0]


def update_income_source(client: Client, user_id: str, source_id: str, payload: dict):
    res = client.table("income_sources").update(payload).eq("user_id", user_id).eq("id", source_id).execute()
    data = res.data or []
    return data[0] if data else None


def delete_income_source(client: Client, user_id: str, source_id: str):
    client.table("income_sources").delete().eq("user_id", user_id).eq("id", source_id).execute()
    return True
