from supabase import Client


def list_accounts(client: Client, user_id: str):
    res = client.table("accounts").select("*").eq("user_id", user_id).order("created_at").execute()
    return res.data or []


def create_account(client: Client, user_id: str, payload: dict):
    payload["user_id"] = user_id
    res = client.table("accounts").insert(payload).execute()
    return (res.data or [None])[0]


def get_account(client: Client, user_id: str, account_id: str):
    res = client.table("accounts").select("*").eq("user_id", user_id).eq("id", account_id).limit(1).execute()
    data = res.data or []
    return data[0] if data else None


def update_account(client: Client, user_id: str, account_id: str, payload: dict):
    res = client.table("accounts").update(payload).eq("user_id", user_id).eq("id", account_id).execute()
    data = res.data or []
    return data[0] if data else None


def archive_account(client: Client, user_id: str, account_id: str):
    return update_account(client, user_id, account_id, {"is_active": False, "archived_at": "now()"})
