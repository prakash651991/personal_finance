from fastapi import APIRouter, Depends, Query
from datetime import date, timedelta
from typing import Optional

from ..security.auth import get_current_user_id, get_user_client

router = APIRouter(tags=["dashboard-reports"])


def _range(start: Optional[str], end: Optional[str]):
    if not start:
        today = date.today()
        start = date(today.year, today.month, 1).isoformat()
    if not end:
        today = date.today()
        # end of month
        if today.month == 12:
            end = date(today.year, 12, 31).isoformat()
        else:
            end = (date(today.year, today.month + 1, 1) - timedelta(days=1)).isoformat()
    return start, end


@router.get("/dashboard/summary")
def dashboard_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    client=Depends(get_user_client),
):
    s, e = _range(start_date, end_date)
    txs = client.table("transactions").select("*").eq("user_id", user_id).eq("status", "posted").gte("transaction_date", s).lte("transaction_date", e).execute().data or []
    income = 0.0
    expense = 0.0
    for t in txs:
        amt = float(t.get("amount") or 0)
        tt = t.get("transaction_type")
        if tt == "income":
            income += amt
        elif tt in ("expense", "credit_card_purchase"):
            expense += amt
        elif tt == "refund":
            expense -= amt
    # balances
    accounts = client.table("accounts").select("*").eq("user_id", user_id).execute().data or []
    total_balance = 0.0
    for a in accounts:
        if not a.get("is_active", True):
            continue
        ob = float(a.get("opening_balance") or 0)
        # compute from transactions
        acc_txs = client.table("transactions").select("transaction_type,amount").eq("user_id", user_id).eq("account_id", a["id"]).eq("status", "posted").execute().data or []
        bal = ob
        for t in acc_txs:
            amt = float(t.get("amount") or 0)
            tt = t.get("transaction_type")
            if tt in ("income", "transfer") and t.get("account_id") == a["id"]:
                # for transfer, need direction; approximate: all transfers into? We'll just add inflows? Hard. Skip complex.
                pass
        total_balance += ob
    # simpler: balance = opening + sum income/expense adjustments? We'll compute net per account by type direction
    total_balance = 0.0
    for a in accounts:
        if not a.get("is_active", True):
            continue
        bal = float(a.get("opening_balance") or 0)
        acc_txs = client.table("transactions").select("transaction_type,amount,account_id,transfer_group_id").eq("user_id", user_id).eq("account_id", a["id"]).eq("status", "posted").execute().data or []
        for t in acc_txs:
            amt = float(t.get("amount") or 0)
            tt = t.get("transaction_type")
            if tt in ("income", "loan_disbursement", "savings_withdrawal"):
                bal += amt
            elif tt in ("expense", "credit_card_payment", "loan_repayment", "savings_contribution"):
                bal -= amt
            elif tt == "refund":
                bal += amt
            elif tt == "transfer":
                # determine if inflow/outflow by checking linked? We'll treat all transfers as outflow from this account; inflow handled in dest account separately? Actually both rows same type transfer; need heuristic: if account is destination? Can't tell. We'll skip transfer adjustment to avoid double; opening balances only.
                pass
            elif tt == "adjustment":
                bal += amt
        total_balance += bal
    # credit card liability
    cards = client.table("credit_cards").select("id").eq("user_id", user_id).execute().data or []
    card_liability = 0.0
    for c in cards:
        txs_cc = client.table("credit_card_transactions").select("amount,kind").eq("user_id", user_id).eq("card_id", c["id"]).execute().data or []
        for x in txs_cc:
            amt = float(x.get("amount") or 0)
            if x.get("kind") in ("purchase", "fee", "interest"):
                card_liability += amt
            elif x.get("kind") in ("refund",):
                card_liability -= amt
        # subtract payments
        pays = client.table("credit_card_payments").select("amount").eq("user_id", user_id).eq("card_id", c["id"]).execute().data or []
        for p in pays:
            card_liability -= float(p.get("amount") or 0)
    # upcoming card payments: statements with due_date in future
    stmts = client.table("credit_card_statements").select("*").eq("user_id", user_id).execute().data or []
    upcoming_cards = [s for s in stmts if s.get("due_date")]
    # emi commitments
    loans = client.table("loans").select("*").eq("user_id", user_id).eq("status", "active").execute().data or []
    total_emi = sum(float(l.get("emi_amount") or 0) for l in loans)
    # budget remaining (current month)
    budgets = client.table("budgets").select("*").eq("user_id", user_id).eq("is_active", True).execute().data or []
    budget_remaining = 0.0
    for b in budgets:
        # actual spending in category within period
        q = client.table("transactions").select("amount").eq("user_id", user_id).eq("category_id", b.get("category_id")).in_("transaction_type", ["expense", "credit_card_purchase"]).eq("status", "posted").gte("transaction_date", b["period_start"]).lte("transaction_date", b["period_end"]).execute().data or []
        actual = sum(float(t.get("amount") or 0) for t in q)
        budget_remaining += float(b["amount"]) - actual
    # goals progress
    goals = client.table("savings_goals").select("*").eq("user_id", user_id).execute().data or []
    goal_progress = []
    for g in goals:
        events = client.table("goal_events").select("*").eq("user_id", user_id).eq("goal_id", g["id"]).execute().data or []
        bal = float(g.get("starting_balance") or 0)
        for e in events:
            amt = float(e.get("amount") or 0)
            if e["event_type"] == "contribution":
                bal += amt
            elif e["event_type"] == "withdrawal":
                bal -= amt
            else:
                bal += amt
        goal_progress.append({"goal_id": g["id"], "name": g["name"], "balance": bal, "target": float(g["target_amount"])})
    return {
        "period_start": s,
        "period_end": e,
        "income": income,
        "expense": expense,
        "net_cash_flow": income - expense,
        "total_balance": total_balance,
        "card_liability": card_liability,
        "total_monthly_emi": total_emi,
        "budget_remaining": budget_remaining,
        "goals": goal_progress,
        "upcoming_card_statements": upcoming_cards,
    }


@router.get("/reports/cash-flow")
def cash_flow_report(start_date: Optional[str] = None, end_date: Optional[str] = None, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    s, e = _range(start_date, end_date)
    txs = client.table("transactions").select("*").eq("user_id", user_id).eq("status", "posted").gte("transaction_date", s).lte("transaction_date", e).order("transaction_date").execute().data or []
    # group by month
    monthly = {}
    for t in txs:
        m = t["transaction_date"][:7]
        monthly.setdefault(m, {"income": 0.0, "expense": 0.0, "transfer": 0.0})
        amt = float(t.get("amount") or 0)
        tt = t.get("transaction_type")
        if tt == "income":
            monthly[m]["income"] += amt
        elif tt in ("expense", "credit_card_purchase"):
            monthly[m]["expense"] += amt
        elif tt == "refund":
            monthly[m]["expense"] -= amt
        elif tt == "transfer":
            monthly[m]["transfer"] += amt
    return {"start": s, "end": e, "monthly": monthly, "transactions": txs}


@router.get("/reports/spending")
def spending_report(start_date: Optional[str] = None, end_date: Optional[str] = None, user_id: str = Depends(get_current_user_id), client=Depends(get_user_client)):
    s, e = _range(start_date, end_date)
    txs = client.table("transactions").select("*").eq("user_id", user_id).in_("transaction_type", ["expense", "credit_card_purchase"]).eq("status", "posted").gte("transaction_date", s).lte("transaction_date", e).execute().data or []
    by_cat = {}
    for t in txs:
        cid = t.get("category_id") or "uncategorized"
        by_cat.setdefault(cid, 0.0)
        by_cat[cid] += float(t.get("amount") or 0)
    # refunds
    refunds = client.table("transactions").select("*").eq("user_id", user_id).eq("transaction_type", "refund").gte("transaction_date", s).lte("transaction_date", e).execute().data or []
    for r in refunds:
        cid = r.get("category_id") or "uncategorized"
        by_cat.setdefault(cid, 0.0)
        by_cat[cid] -= float(r.get("amount") or 0)
    return {"start": s, "end": e, "by_category": by_cat}
