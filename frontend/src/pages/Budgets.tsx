import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

export default function Budgets() {
  const [budgets, setBudgets] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [editing, setEditing] = useState<string | null>(null);
  const [form, setForm] = useState({ category_id: "", amount: "", period_start: new Date().toISOString().slice(0, 10), period_end: new Date().toISOString().slice(0, 10) });
  const load = () => {
    apiFetch("/api/v1/budgets").then(setBudgets).catch(console.error);
    apiFetch("/api/v1/categories").then(setCategories).catch(console.error);
  };
  useEffect(() => { load(); }, []);
  const reset = () => { setEditing(null); setForm({ category_id: "", amount: "", period_start: new Date().toISOString().slice(0, 10), period_end: new Date().toISOString().slice(0, 10) }); };
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const body = { ...form, amount: parseFloat(form.amount) };
    if (editing) await apiFetch(`/api/v1/budgets/${editing}`, { method: "PATCH", body: JSON.stringify(body) });
    else await apiFetch("/api/v1/budgets", { method: "POST", body: JSON.stringify(body) });
    reset(); load();
  };
  const edit = (b: any) => { setEditing(b.id); setForm({ category_id: b.category_id || "", amount: String(b.amount), period_start: b.period_start, period_end: b.period_end }); };
  const del = async (id: string) => { if (!confirm("Delete?")) return; await apiFetch(`/api/v1/budgets/${id}`, { method: "DELETE" }); load(); };
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Budgets</h2>
      <div className="card">
        <form onSubmit={submit} className="grid">
          <div><div className="label">Category</div><select value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}><option value="">Category</option>{categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select></div>
          <div><div className="label">Amount</div><input value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} placeholder="Amount" /></div>
          <div className="row">
            <div style={{ flex: 1 }}><div className="label">Period start</div><input type="date" value={form.period_start} onChange={(e) => setForm({ ...form, period_start: e.target.value })} /></div>
            <div style={{ flex: 1 }}><div className="label">Period end</div><input type="date" value={form.period_end} onChange={(e) => setForm({ ...form, period_end: e.target.value })} /></div>
          </div>
          <div className="row">
            <button type="submit">{editing ? "Update" : "Add"} budget</button>
            {editing && <button type="button" className="secondary" onClick={reset}>Cancel</button>}
          </div>
        </form>
      </div>
      <div className="card">
        <ul className="list">
          {budgets.map((b) => (
            <li key={b.id}>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <div>{b.amount} · {b.period_start} → {b.period_end}</div>
                <div className="row">
                  <button className="secondary" onClick={() => edit(b)}>Edit</button>
                  <button className="danger" onClick={() => del(b.id)}>Del</button>
                </div>
              </div>
            </li>
          ))}
          {budgets.length === 0 && <li>No budgets yet</li>}
        </ul>
      </div>
    </div>
  );
}
