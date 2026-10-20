from supabase import Client


def get_profile(client: Client, user_id: str):
    res = client.table("profiles").select("*").eq("id", user_id).limit(1).execute()
    data = res.data or []
    if data:
        return data[0]
    # create default
    res = client.table("profiles").insert({"id": user_id}).execute()
    return (res.data or [None])[0]


def update_profile(client: Client, user_id: str, payload: dict):
    # ensure exists
    get_profile(client, user_id)
    res = client.table("profiles").update(payload).eq("id", user_id).execute()
    data = res.data or []
    return data[0] if data else None
