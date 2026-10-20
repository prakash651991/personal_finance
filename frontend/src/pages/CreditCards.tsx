import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

export default function CreditCards() {
  const [cards, setCards] = useState<any[]>([]);
  const [editing, setEditing] = useState<string | null>(null);
  const [form, setForm] = useState({ nickname: "", issuer: "", statement_day: "20", due_day: "10", credit_limit: "" });
  const [selected, setSelected] = useState<string | null>(null);
  const [stmts, setStmts] = useState<any[]>([]);
  const [unbilled, setUnbilled] = useState<any[]>([]);
  const load = () => apiFetch("/api/v1/credit-cards").then(setCards).catch(console.error);
  useEffect(() => { load(); }, []);
  const reset = () => { setEditing(null); setForm({ nickname: "", issuer: "", statement_day: "20", due_day: "10", credit_limit: "" }); };
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const body: any = { ...form, statement_day: parseInt(form.statement_day), due_day: parseInt(form.due_day), credit_limit: form.credit_limit ? parseFloat(form.credit_limit) : undefined };
    if (editing) await apiFetch(`/api/v1/credit-cards/${editing}`, { method: "PATCH", body: JSON.stringify(body) });
    else await apiFetch("/api/v1/credit-cards", { method: "POST", body: JSON.stringify(body) });
    reset(); load();
  };
  const edit = (c: any) => { setEditing(c.id); setForm({ nickname: c.nickname, issuer: c.issuer || "", statement_day: String(c.statement_day || 20), due_day: String(c.due_day || 10), credit_limit: c.credit_limit ? String(c.credit_limit) : "" }); };
  const del = async (id: string) => { if (!confirm("Delete?")) return; await apiFetch(`/api/v1/credit-cards/${id}`, { method: "DELETE" }); load(); };
  const selectCard = async (id: string) => {
    setSelected(id);
    setStmts(await apiFetch(`/api/v1/credit-cards/${id}/statements`));
    setUnbilled(await apiFetch(`/api/v1/credit-cards/${id}/unbilled`));
  };
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Credit Cards</h2>
      <div className="card">
        <form onSubmit={submit} className="grid">
          <div><div className="label">Nickname</div><input value={form.nickname} onChange={(e) => setForm({ ...form, nickname: e.target.value })} placeholder="Nickname" /></div>
          <div><div className="label">Issuer</div><input value={form.issuer} onChange={(e) => setForm({ ...form, issuer: e.target.value })} placeholder="Issuer" /></div>
          <div className="row">
            <div style={{ flex: 1 }}><div className="label">Statement day</div><input value={form.statement_day} onChange={(e) => setForm({ ...form, statement_day: e.target.value })} placeholder="Statement day" /></div>
            <div style={{ flex: 1 }}><div className="label">Due day</div><input value={form.due_day} onChange={(e) => setForm({ ...form, due_day: e.target.value })} placeholder="Due day" /></div>
          </div>
          <div><div className="label">Credit limit</div><input value={form.credit_limit} onChange={(e) => setForm({ ...form, credit_limit: e.target.value })} placeholder="Credit limit" /></div>
          <div className="row">
            <button type="submit">{editing ? "Update" : "Add"} card</button>
            {editing && <button type="button" className="secondary" onClick={reset}>Cancel</button>}
          </div>
        </form>
      </div>
      <div className="card">
        <ul className="list">
          {cards.map((c) => (
            <li key={c.id}>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <button className="secondary" style={{ flex: 1 }} onClick={() => selectCard(c.id)}>{c.nickname} {c.last4 ? `••${c.last4}` : ""}</button>
                <button className="secondary" onClick={() => edit(c)}>Edit</button>
                <button className="danger" onClick={() => del(c.id)}>Del</button>
              </div>
            </li>
          ))}
          {cards.length === 0 && <li>No cards yet</li>}
        </ul>
      </div>
      {selected && (
        <>
          <div className="card">
            <h3 style={{ marginTop: 0 }}>Statements</h3>
            <ul className="list">
              {stmts.map((s) => <li key={s.id}>{s.period_start} → {s.period_end} · total {s.statement_total} · due {s.due_date} · paid {s.paid_amount}</li>)}
              {stmts.length === 0 && <li>No statements</li>}
            </ul>
          </div>
          <div className="card">
            <h3 style={{ marginTop: 0 }}>Unbilled</h3>
            <ul className="list">
              {unbilled.map((u) => <li key={u.id}>{u.purchase_date} · {u.amount} · {u.description}</li>)}
              {unbilled.length === 0 && <li>No unbilled activity</li>}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
