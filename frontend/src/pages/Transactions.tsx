import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

export default function Transactions() {
  const [txs, setTxs] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [cards, setCards] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [occurrences, setOccurrences] = useState<any[]>([]);
  const [recurring, setRecurring] = useState<any[]>([]);
  const [occurrenceId, setOccurrenceId] = useState("");
  const [pendingOcc, setPendingOcc] = useState<string | null>(null);
  const [editing, setEditing] = useState<string | null>(null);
  const [form, setForm] = useState({ transaction_type: "expense", amount: "", transaction_date: new Date().toISOString().slice(0, 10), account_id: "", card_id: "", category_id: "", description: "" });

  const load = () => {
    apiFetch("/api/v1/transactions").then(setTxs).catch(console.error);
    apiFetch("/api/v1/accounts").then(async (rows) => {
      let list = rows || [];
      if (list.length === 0) {
        const created = await apiFetch("/api/v1/accounts", { method: "POST", body: JSON.stringify({ name: "Cash", account_type: "cash", opening_balance: 0 }) });
        list = [created];
      }
      setAccounts(list);
      const cash = list.find((a: any) => a.account_type === "cash") || list[0];
      if (cash) setForm((f) => (f.account_id || f.card_id ? f : { ...f, account_id: cash.id }));
    }).catch(console.error);
    apiFetch("/api/v1/credit-cards").then(setCards).catch(console.error);
    apiFetch("/api/v1/categories").then(setCategories).catch(console.error);
    const cm = new Date().toISOString().slice(0, 7);
    apiFetch("/api/v1/recurring-expenses/occurrences").then((rows) => setOccurrences((rows || []).filter((r: any) => r.status === "expected" && String(r.due_date).startsWith(cm)))).catch(console.error);
    apiFetch("/api/v1/recurring-expenses").then(setRecurring).catch(console.error);
  };
  useEffect(() => { load(); const occ = new URLSearchParams(window.location.search).get("occ"); if (occ) setPendingOcc(occ); }, []);
  const reset = () => { setEditing(null); setOccurrenceId(""); setForm({ transaction_type: "expense", amount: "", transaction_date: new Date().toISOString().slice(0, 10), account_id: "", card_id: "", category_id: "", description: "" }); };
  useEffect(() => {
    if (!pendingOcc || occurrences.length === 0) return;
    const occ = occurrences.find((o) => o.id === pendingOcc);
    if (occ) {
      const r = recurring.find((x) => x.id === occ.recurring_expense_id);
      setOccurrenceId(occ.id);
      setForm((f) => ({ ...f, transaction_type: "expense", amount: String(occ.expected_amount), description: r ? r.name : f.description, category_id: r?.category_id || f.category_id }));
    }
    setPendingOcc(null);
  }, [pendingOcc, occurrences, recurring]);
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (!form.amount || isNaN(parseFloat(form.amount))) { (window as any).showToast?.("Enter amount"); return; }
      const body: any = { ...form, amount: parseFloat(form.amount) };
      if (!editing && occurrenceId) body.recurring_occurrence_id = occurrenceId;
      if (editing) await apiFetch(`/api/v1/transactions/${editing}`, { method: "PATCH", body: JSON.stringify(body) });
      else await apiFetch("/api/v1/transactions", { method: "POST", body: JSON.stringify(body) });
      (window as any).showToast?.("Transaction saved");
      reset(); load();
    } catch (e: any) {
      console.error(e);
      (window as any).showToast?.("Failed: " + (e?.message || "error"));
    }
  };
  const edit = (t: any) => {
    setEditing(t.id);
    setForm({ transaction_type: t.transaction_type, amount: String(t.amount), transaction_date: t.transaction_date, account_id: t.account_id || "", card_id: t.card_id || "", category_id: t.category_id || "", description: t.description || "" });
  };
  const del = async (id: string) => { if (!confirm("Reverse/delete?")) return; await apiFetch(`/api/v1/transactions/${id}`, { method: "DELETE" }); load(); };

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Transactions</h2>
      <div className="card">
        <form onSubmit={submit} className="grid">
          <div><div className="label">Type</div><select value={form.transaction_type} onChange={(e) => setForm({ ...form, transaction_type: e.target.value })}><option value="expense">Expense</option><option value="income">Income</option></select></div>
          <div><div className="label">Amount</div><input value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} placeholder="Amount" /></div>
          <div><div className="label">Date</div><input type="date" value={form.transaction_date} onChange={(e) => setForm({ ...form, transaction_date: e.target.value })} /></div>
          <div><div className="label">Account / Credit card</div><select value={form.account_id ? `a:${form.account_id}` : form.card_id ? `c:${form.card_id}` : ""} onChange={(e) => {
            const v = e.target.value;
            if (v.startsWith("a:")) setForm({ ...form, account_id: v.slice(2), card_id: "" });
            else if (v.startsWith("c:")) setForm({ ...form, card_id: v.slice(2), account_id: "" });
            else setForm({ ...form, account_id: "", card_id: "" });
          }}><option value="">Select account/card</option>{accounts.map((a) => <option key={a.id} value={`a:${a.id}`}>{a.name} (account)</option>)}{cards.map((c) => <option key={c.id} value={`c:${c.id}`}>{c.nickname} (card)</option>)}</select></div>
          <div><div className="label">Category</div><select value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}><option value="">Category</option>{categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select></div>
          <div><div className="label">Description</div><input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Description" /></div>
          {!editing && (
            <div><div className="label">Link recurring (current month)</div><select value={occurrenceId} onChange={(e) => {
              const id = e.target.value;
              setOccurrenceId(id);
              const occ = occurrences.find((o) => o.id === id);
              if (occ) {
                const r = recurring.find((x) => x.id === occ.recurring_expense_id);
                setForm((f) => ({ ...f, amount: String(occ.expected_amount), description: r ? r.name : f.description, category_id: r?.category_id || f.category_id }));
              }
            }}><option value="">Link recurring (optional)</option>{occurrences.map((o) => { const r = recurring.find((x) => x.id === o.recurring_expense_id); return <option key={o.id} value={o.id}>{r ? r.name : "Recurring"} · {o.expected_amount} · due {o.due_date}</option>; })}</select></div>
          )}
          <div className="row">
            <button type="submit">{editing ? "Update" : "Add"} transaction</button>
            {editing && <button type="button" className="secondary" onClick={reset}>Cancel</button>}
          </div>
        </form>
      </div>

      <div className="card">
        <ul className="list">
          {txs.map((t) => (
            <li key={t.id}>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <div>
                  <div style={{ fontWeight: 600 }}>{t.description || t.transaction_type}</div>
                  <div className="label">{t.transaction_date} · {t.transaction_type} · {t.amount}</div>
                </div>
                <div className="row">
                  <button className="secondary" onClick={() => edit(t)}>Edit</button>
                  <button className="danger" onClick={() => del(t.id)}>Del</button>
                </div>
              </div>
            </li>
          ))}
          {txs.length === 0 && <li>No transactions yet</li>}
        </ul>
      </div>
    </div>
  );
}
