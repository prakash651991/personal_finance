from supabase import Client
from datetime import date


def _add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    day = d.day
    # clamp day to month length
    if m == 2:
        max_day = 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28
    elif m in (4, 6, 9, 11):
        max_day = 30
    else:
        max_day = 31
    if day > max_day:
        day = max_day
    return date(y, m, day)


def list_loans(client: Client, user_id: str):
    res = client.table("loans").select("*").eq("user_id", user_id).execute()
    return res.data or []


def create_loan(client: Client, user_id: str, payload: dict):
    payload["user_id"] = user_id
    if not payload.get("first_emi_date"):
        payload["first_emi_date"] = payload["start_date"]
    # normalize dates
    for k in ("start_date", "end_date", "first_emi_date"):
        if payload.get(k):
            payload[k] = str(payload[k])
    res = client.table("loans").insert(payload).execute()
    loan = (res.data or [None])[0]
    if loan:
        generate_installments(client, user_id, loan)
    return loan


def generate_installments(client: Client, user_id: str, loan: dict):
    # remove existing upcoming installments? For new loan only
    first = loan.get("first_emi_date")
    if isinstance(first, str):
        first = date.fromisoformat(first)
    end = loan["end_date"]
    if isinstance(end, str):
        end = date.fromisoformat(end)
    emi = float(loan["emi_amount"])
    # check existing
    existing = client.table("loan_installments").select("id").eq("loan_id", loan["id"]).execute().data or []
    if existing:
        return existing
    rows = []
    num = 1
    cur_date = first
    while cur_date <= end:
        rows.append({
            "user_id": user_id,
            "loan_id": loan["id"],
            "installment_number": num,
            "due_date": str(cur_date),
            "expected_amount": emi,
            "paid_amount": 0,
            "status": "upcoming",
        })
        num += 1
        cur_date = _add_months(cur_date, 1)
        if num > 600:
            break
    if rows:
        client.table("loan_installments").insert(rows).execute()
    return rows


def list_installments(client: Client, user_id: str, loan_id: str):
    res = client.table("loan_installments").select("*").eq("user_id", user_id).eq("loan_id", loan_id).order("installment_number").execute()
    return res.data or []


def get_loan(client: Client, user_id: str, loan_id: str):
    res = client.table("loans").select("*").eq("user_id", user_id).eq("id", loan_id).limit(1).execute()
    data = res.data or []
    return data[0] if data else None


def update_loan(client: Client, user_id: str, loan_id: str, payload: dict):
    if payload.get("end_date"):
        payload["end_date"] = str(payload["end_date"])
    res = client.table("loans").update(payload).eq("user_id", user_id).eq("id", loan_id).execute()
    data = res.data or []
    return data[0] if data else None


def archive_loan(client: Client, user_id: str, loan_id: str):
    return update_loan(client, user_id, loan_id, {"status": "archived"})


def delete_payment(client: Client, user_id: str, payment_id: str):
    client.table("loan_payments").delete().eq("user_id", user_id).eq("id", payment_id).execute()
    return True


def update_installment(client: Client, user_id: str, installment_id: str, payload: dict):
    if payload.get("due_date"):
        payload["due_date"] = str(payload["due_date"])
    if payload.get("paid_date"):
        payload["paid_date"] = str(payload["paid_date"])
    res = client.table("loan_installments").update(payload).eq("user_id", user_id).eq("id", installment_id).execute()
    data = res.data or []
    return data[0] if data else None


def delete_installment(client: Client, user_id: str, installment_id: str):
    client.table("loan_installments").delete().eq("user_id", user_id).eq("id", installment_id).execute()
    return True


def record_payment(client: Client, user_id: str, loan_id: str, payload: dict):
    # canonical transaction
    tx_id = None
    if payload.get("account_id"):
        tx_payload = {
            "user_id": user_id,
            "account_id": payload["account_id"],
            "transaction_type": "loan_repayment",
            "amount": payload["amount"],
            "transaction_date": str(payload["payment_date"]),
            "description": payload.get("notes") or "Loan payment",
            "status": "posted",
        }
        res = client.table("transactions").insert(tx_payload).execute()
        tx = (res.data or [None])[0]
        tx_id = tx["id"] if tx else None
    # loan_payment row
    lp = {
        "user_id": user_id,
        "loan_id": loan_id,
        "installment_id": payload.get("installment_id"),
        "transaction_id": tx_id,
        "payment_date": str(payload["payment_date"]),
        "amount": payload["amount"],
        "notes": payload.get("notes"),
    }
    res = client.table("loan_payments").insert(lp).execute()
    payment = (res.data or [None])[0]
    # update installment if linked
    if payload.get("installment_id"):
        inst = client.table("loan_installments").select("paid_amount,expected_amount").eq("id", payload["installment_id"]).limit(1).execute()
        if inst.data:
            paid = float(inst.data[0].get("paid_amount") or 0) + float(payload["amount"])
            expected = float(inst.data[0].get("expected_amount") or 0)
            status = "paid" if paid >= expected - 0.005 else "partial"
            client.table("loan_installments").update({"paid_amount": paid, "paid_date": str(payload["payment_date"]), "status": status, "transaction_id": tx_id}).eq("id", payload["installment_id"]).execute()
    return {"payment": payment, "transaction_id": tx_id}


def reschedule_preview(client: Client, user_id: str, loan_id: str, new_end_date: str, new_emi: float | None):
    loan = get_loan(client, user_id, loan_id)
    if not loan:
        return None
    first = loan.get("first_emi_date")
    if isinstance(first, str):
        first = date.fromisoformat(first)
    # find last paid installment
    insts = list_installments(client, user_id, loan_id)
    paid_nums = [i["installment_number"] for i in insts if i.get("status") in ("paid", "partial")]
    last_paid = max(paid_nums) if paid_nums else 0
    # generate future dates
    end = date.fromisoformat(new_end_date)
    # start from first unpaid installment date
    unpaid = [i for i in insts if i["installment_number"] > last_paid]
    start_date = date.fromisoformat(unpaid[0]["due_date"]) if unpaid else _add_months(first, last_paid)
    future = []
    num = last_paid + 1
    cur = start_date
    emi = new_emi if new_emi else float(loan["emi_amount"])
    while cur <= end:
        future.append({"installment_number": num, "due_date": str(cur), "expected_amount": emi})
        num += 1
        cur = _add_months(cur, 1)
    return {"preserved_paid_count": last_paid, "future": future}


def reschedule_confirm(client: Client, user_id: str, loan_id: str, new_end_date: str, new_emi: float | None):
    loan = get_loan(client, user_id, loan_id)
    if not loan:
        return None
    # delete future installments (unpaid)
    insts = list_installments(client, user_id, loan_id)
    for i in insts:
        if i.get("status") not in ("paid", "partial"):
            client.table("loan_installments").delete().eq("id", i["id"]).execute()
    preview = reschedule_preview(client, user_id, loan_id, new_end_date, new_emi)
    if not preview:
        return None
    rows = []
    for f in preview["future"]:
        rows.append({
            "user_id": user_id,
            "loan_id": loan_id,
            "installment_number": f["installment_number"],
            "due_date": f["due_date"],
            "expected_amount": f["expected_amount"],
            "paid_amount": 0,
            "status": "upcoming",
        })
    if rows:
        client.table("loan_installments").insert(rows).execute()
    update_loan(client, user_id, loan_id, {"end_date": new_end_date, "emi_amount": new_emi if new_emi else loan["emi_amount"]})
    return preview
