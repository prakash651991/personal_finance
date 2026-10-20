from supabase import Client


def list_categories(client: Client, user_id: str):
    res = client.table("categories").select("*").or_(f"user_id.eq.{user_id},user_id.is.null").execute()
    return res.data or []


def create_category(client: Client, user_id: str, payload: dict):
    payload["user_id"] = user_id
    res = client.table("categories").insert(payload).execute()
    return (res.data or [None])[0]


def update_category(client: Client, user_id: str, category_id: str, payload: dict):
    res = client.table("categories").update(payload).eq("user_id", user_id).eq("id", category_id).execute()
    data = res.data or []
    return data[0] if data else None


def delete_category(client: Client, user_id: str, category_id: str):
    res = client.table("categories").delete().eq("user_id", user_id).eq("id", category_id).execute()
    return True
