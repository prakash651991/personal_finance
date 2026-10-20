from supabase import Client
from uuid import uuid4


def list_transactions(client: Client, user_id: str, filters: dict | None = None):
    q = client.table("transactions").select("*").eq("user_id", user_id)
    if filters:
        if filters.get("transaction_type"):
            q = q.eq("transaction_type", filters["transaction_type"])
        if filters.get("account_id"):
            q = q.eq("account_id", filters["account_id"])
        if filters.get("category_id"):
            q = q.eq("category_id", filters["category_id"])
        if filters.get("start_date"):
            q = q.gte("transaction_date", filters["start_date"])
        if filters.get("end_date"):
            q = q.lte("transaction_date", filters["end_date"])
    res = q.order("transaction_date", desc=True).limit(500).execute()
    return res.data or []


def create_transaction(client: Client, user_id: str, payload: dict):
    occ_id = payload.pop("recurring_occurrence_id", None)
    card_id = payload.pop("card_id", None)
    payload["user_id"] = user_id
    # if card provided, treat as credit card purchase
    if card_id and payload.get("transaction_type") not in ("credit_card_purchase",):
        payload["transaction_type"] = "credit_card_purchase"
    res = client.table("transactions").insert(payload).execute()
    tx = (res.data or [None])[0]
    if tx and occ_id:
        client.table("recurring_occurrences").update({"status": "paid", "transaction_id": tx["id"]}).eq("id", occ_id).eq("user_id", user_id).execute()
    if tx and card_id:
        client.table("credit_card_transactions").insert({
            "user_id": user_id,
            "card_id": card_id,
            "transaction_id": tx["id"],
            "kind": "purchase",
            "purchase_date": payload.get("transaction_date"),
            "amount": payload.get("amount"),
            "description": payload.get("description"),
        }).execute()
    return tx


def get_transaction(client: Client, user_id: str, tx_id: str):
    res = client.table("transactions").select("*").eq("user_id", user_id).eq("id", tx_id).limit(1).execute()
    data = res.data or []
    return data[0] if data else None


def update_transaction(client: Client, user_id: str, tx_id: str, payload: dict):
    res = client.table("transactions").update(payload).eq("user_id", user_id).eq("id", tx_id).execute()
    data = res.data or []
    return data[0] if data else None


def delete_transaction(client: Client, user_id: str, tx_id: str):
    # soft: mark reversed
    return update_transaction(client, user_id, tx_id, {"status": "reversed"})


def create_transfer(client: Client, user_id: str, source_account_id: str, dest_account_id: str, amount: float, tx_date, description=None):
    group_id = str(uuid4())
    outflow = {
        "user_id": user_id,
        "account_id": source_account_id,
        "transaction_type": "transfer",
        "amount": amount,
        "transaction_date": str(tx_date),
        "description": description,
        "transfer_group_id": group_id,
        "status": "posted",
    }
    inflow = {
        "user_id": user_id,
        "account_id": dest_account_id,
        "transaction_type": "transfer",
        "amount": amount,
        "transaction_date": str(tx_date),
        "description": description,
        "transfer_group_id": group_id,
        "linked_transaction_id": None,
        "status": "posted",
    }
    res1 = client.table("transactions").insert(outflow).execute()
    r1 = (res1.data or [None])[0]
    if r1:
        inflow["linked_transaction_id"] = r1["id"]
    res2 = client.table("transactions").insert(inflow).execute()
    r2 = (res2.data or [None])[0]
    if r1 and r2:
        client.table("transactions").update({"linked_transaction_id": r2["id"]}).eq("id", r1["id"]).execute()
    return {"outflow": r1, "inflow": r2, "transfer_group_id": group_id}
