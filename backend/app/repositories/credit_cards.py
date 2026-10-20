from supabase import Client
from datetime import date, timedelta


def list_cards(client: Client, user_id: str):
    res = client.table("credit_cards").select("*").eq("user_id", user_id).execute()
    return res.data or []


def create_card(client: Client, user_id: str, payload: dict):
    payload["user_id"] = user_id
    res = client.table("credit_cards").insert(payload).execute()
    return (res.data or [None])[0]


def list_statements(client: Client, user_id: str, card_id: str):
    res = client.table("credit_card_statements").select("*").eq("user_id", user_id).eq("card_id", card_id).order("period_start", desc=True).execute()
    return res.data or []


def create_statement(client: Client, user_id: str, payload: dict):
    payload["user_id"] = user_id
    res = client.table("credit_card_statements").insert(payload).execute()
    return (res.data or [None])[0]


def list_unbilled(client: Client, user_id: str, card_id: str):
    res = client.table("credit_card_transactions").select("*").eq("user_id", user_id).eq("card_id", card_id).is_("statement_id", "null").execute()
    return res.data or []


def create_cc_transaction(client: Client, user_id: str, payload: dict):
    payload["user_id"] = user_id
    res = client.table("credit_card_transactions").insert(payload).execute()
    return (res.data or [None])[0]


def update_card(client: Client, user_id: str, card_id: str, payload: dict):
    res = client.table("credit_cards").update(payload).eq("user_id", user_id).eq("id", card_id).execute()
    data = res.data or []
    return data[0] if data else None


def delete_card(client: Client, user_id: str, card_id: str):
    client.table("credit_cards").delete().eq("user_id", user_id).eq("id", card_id).execute()
    return True


def update_statement(client: Client, user_id: str, statement_id: str, payload: dict):
    for k in ("period_start", "period_end", "statement_date", "due_date"):
        if payload.get(k):
            payload[k] = str(payload[k])
    res = client.table("credit_card_statements").update(payload).eq("user_id", user_id).eq("id", statement_id).execute()
    data = res.data or []
    return data[0] if data else None


def delete_statement(client: Client, user_id: str, statement_id: str):
    client.table("credit_card_statements").delete().eq("user_id", user_id).eq("id", statement_id).execute()
    return True


def update_cc_transaction(client: Client, user_id: str, cc_tx_id: str, payload: dict):
    for k in ("purchase_date", "posting_date"):
        if payload.get(k):
            payload[k] = str(payload[k])
    res = client.table("credit_card_transactions").update(payload).eq("user_id", user_id).eq("id", cc_tx_id).execute()
    data = res.data or []
    return data[0] if data else None


def delete_cc_transaction(client: Client, user_id: str, cc_tx_id: str):
    client.table("credit_card_transactions").delete().eq("user_id", user_id).eq("id", cc_tx_id).execute()
    return True


def delete_payment(client: Client, user_id: str, payment_id: str):
    client.table("credit_card_payments").delete().eq("user_id", user_id).eq("id", payment_id).execute()
    return True


def record_payment(client: Client, user_id: str, payload: dict):
    # create canonical transaction (credit_card_payment) in selected account if provided
    tx_id = None
    if payload.get("account_id"):
        tx_payload = {
            "user_id": user_id,
            "account_id": payload["account_id"],
            "transaction_type": "credit_card_payment",
            "amount": payload["amount"],
            "transaction_date": str(payload["payment_date"]),
            "description": payload.get("description") or "Credit card payment",
            "status": "posted",
        }
        res = client.table("transactions").insert(tx_payload).execute()
        tx = (res.data or [None])[0]
        tx_id = tx["id"] if tx else None
    pay_payload = {
        "user_id": user_id,
        "card_id": payload["card_id"],
        "transaction_id": tx_id,
        "statement_id": payload.get("statement_id"),
        "payment_date": str(payload["payment_date"]),
        "amount": payload["amount"],
    }
    res = client.table("credit_card_payments").insert(pay_payload).execute()
    pay = (res.data or [None])[0]
    # update statement paid_amount if linked
    if payload.get("statement_id"):
        st = client.table("credit_card_statements").select("paid_amount").eq("id", payload["statement_id"]).limit(1).execute()
        if st.data:
            new_paid = float(st.data[0].get("paid_amount") or 0) + float(payload["amount"])
            client.table("credit_card_statements").update({"paid_amount": new_paid}).eq("id", payload["statement_id"]).execute()
    return {"payment": pay, "transaction_id": tx_id}
