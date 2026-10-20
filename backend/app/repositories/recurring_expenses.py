from supabase import Client
from datetime import date, timedelta


def _add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    day = min(d.day, 31)
    if m == 2:
        max_day = 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28
    elif m in (4, 6, 9, 11):
        max_day = 30
    else:
        max_day = 31
    if day > max_day:
        day = max_day
    return date(y, m, day)


def list_recurring(client: Client, user_id: str):
    res = client.table("recurring_expenses").select("*").eq("user_id", user_id).execute()
    return res.data or []


def create_recurring(client: Client, user_id: str, payload: dict):
    payload["user_id"] = user_id
    for k in ("first_due_date", "end_date"):
        if payload.get(k):
            payload[k] = str(payload[k])
    res = client.table("recurring_expenses").insert(payload).execute()
    rec = (res.data or [None])[0]
    if rec:
        generate_occurrences(client, user_id, rec)
    return rec


def update_recurring(client: Client, user_id: str, recurring_id: str, payload: dict):
    for k in ("first_due_date", "end_date"):
        if payload.get(k):
            payload[k] = str(payload[k])
    res = client.table("recurring_expenses").update(payload).eq("user_id", user_id).eq("id", recurring_id).execute()
    data = res.data or []
    return data[0] if data else None


def delete_recurring(client: Client, user_id: str, recurring_id: str):
    client.table("recurring_occurrences").delete().eq("user_id", user_id).eq("recurring_expense_id", recurring_id).execute()
    client.table("recurring_expenses").delete().eq("user_id", user_id).eq("id", recurring_id).execute()
    return True


def update_occurrence(client: Client, user_id: str, occurrence_id: str, payload: dict):
    if payload.get("due_date"):
        payload["due_date"] = str(payload["due_date"])
    res = client.table("recurring_occurrences").update(payload).eq("user_id", user_id).eq("id", occurrence_id).execute()
    data = res.data or []
    return data[0] if data else None


def delete_occurrence(client: Client, user_id: str, occurrence_id: str):
    client.table("recurring_occurrences").delete().eq("user_id", user_id).eq("id", occurrence_id).execute()
    return True


def generate_occurrences(client: Client, user_id: str, rec: dict):
    first = date.fromisoformat(rec["first_due_date"]) if isinstance(rec["first_due_date"], str) else rec["first_due_date"]
    end = rec.get("end_date")
    end_d = date.fromisoformat(end) if isinstance(end, str) and end else end
    freq = rec["frequency"]
    cur = first
    rows = []
    seen = set()
    # existing
    ex = client.table("recurring_occurrences").select("due_date").eq("recurring_expense_id", rec["id"]).execute().data or []
    for e in ex:
        seen.add(e["due_date"])
    count = 0
    max_occ = 365 if end_d is not None else 60
    while (end_d is None or cur <= end_d) and count < max_occ:
        ds = str(cur)
        if ds not in seen:
            rows.append({
                "user_id": user_id,
                "recurring_expense_id": rec["id"],
                "due_date": ds,
                "expected_amount": rec["expected_amount"],
                "status": "expected",
            })
            seen.add(ds)
        # increment
        if freq == "daily":
            cur = cur + timedelta(days=1)
        elif freq == "weekly":
            cur = cur + timedelta(days=7)
        elif freq == "monthly":
            cur = _add_months(cur, 1)
        elif freq == "quarterly":
            cur = _add_months(cur, 3)
        elif freq == "yearly":
            cur = _add_months(cur, 12)
        else:
            break
        count += 1
    if rows:
        client.table("recurring_occurrences").insert(rows).execute()
    return rows


def list_occurrences(client: Client, user_id: str, recurring_id: str | None = None):
    q = client.table("recurring_occurrences").select("*").eq("user_id", user_id)
    if recurring_id:
        q = q.eq("recurring_expense_id", recurring_id)
    res = q.order("due_date").execute()
    return res.data or []
