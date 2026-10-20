import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

export default function Recurring() {
  const [items, setItems] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [editing, setEditing] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", expected_amount: "", frequency: "monthly", first_due_date: new Date().toISOString().slice(0, 10), category_id: "" });
  const load = () => apiFetch("/api/v1/recurring-expenses").then(setItems).catch(console.error);
  useEffect(() => { load(); apiFetch("/api/v1/categories").then(setCategories).catch(console.error); }, []);
  const reset = () => { setEditing(null); setForm({ name: "", expected_amount: "", frequency: "monthly", first_due_date: new Date().toISOString().slice(0, 10), category_id: "" }); };
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const body: any = { ...form, expected_amount: parseFloat(form.expected_amount) };
    if (editing) await apiFetch(`/api/v1/recurring-expenses/${editing}`, { method: "PATCH", body: JSON.stringify(body) });
    else await apiFetch("/api/v1/recurring-expenses", { method: "POST", body: JSON.stringify(body) });
    reset(); load();
  };
  const edit = (r: any) => { setEditing(r.id); setForm({ name: r.name, expected_amount: String(r.expected_amount), frequency: r.frequency, first_due_date: r.first_due_date, category_id: r.category_id || "" }); };
  const del = async (id: string) => { if (!confirm("Delete?")) return; await apiFetch(`/api/v1/recurring-expenses/${id}`, { method: "DELETE" }); load(); };
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Recurring Expenses</h2>
      <div className="card">
        <form onSubmit={submit} className="grid">
          <div><div className="label">Name</div><input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Name" /></div>
          <div><div className="label">Amount</div><input value={form.expected_amount} onChange={(e) => setForm({ ...form, expected_amount: e.target.value })} placeholder="Amount" /></div>
          <div><div className="label">Frequency</div><select value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })}><option value="monthly">Monthly</option><option value="weekly">Weekly</option><option value="yearly">Yearly</option></select></div>
          <div><div className="label">Starting date</div><input type="date" value={form.first_due_date} onChange={(e) => setForm({ ...form, first_due_date: e.target.value })} /></div>
          <div><div className="label">Category</div><select value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}><option value="">Category</option>{categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select></div>
          <div className="row">
            <button type="submit">{editing ? "Update" : "Add"} recurring</button>
            {editing && <button type="button" className="secondary" onClick={reset}>Cancel</button>}
          </div>
        </form>
      </div>
      <div className="card">
        <ul className="list">
          {items.map((r) => (
            <li key={r.id}>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <div>{r.name} · {r.expected_amount} · {r.frequency}</div>
                <div className="row">
                  <button className="secondary" onClick={() => edit(r)}>Edit</button>
                  <button className="danger" onClick={() => del(r.id)}>Del</button>
                </div>
              </div>
            </li>
          ))}
          {items.length === 0 && <li>No recurring expenses yet</li>}
        </ul>
      </div>
    </div>
  );
}
