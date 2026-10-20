import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

export default function Gold() {
  const [items, setItems] = useState<any[]>([]);
  const [editing, setEditing] = useState<string | null>(null);
  const [form, setForm] = useState({ purchase_date: new Date().toISOString().slice(0, 10), grams: "", total_cost: "", purity: "" });
  const load = () => apiFetch("/api/v1/gold").then(setItems).catch(console.error);
  useEffect(() => { load(); }, []);
  const reset = () => { setEditing(null); setForm({ purchase_date: new Date().toISOString().slice(0, 10), grams: "", total_cost: "", purity: "" }); };
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const body = { ...form, grams: parseFloat(form.grams), total_cost: parseFloat(form.total_cost) };
    if (editing) await apiFetch(`/api/v1/gold/${editing}`, { method: "PATCH", body: JSON.stringify(body) });
    else await apiFetch("/api/v1/gold", { method: "POST", body: JSON.stringify(body) });
    reset(); load();
  };
  const edit = (g: any) => { setEditing(g.id); setForm({ purchase_date: g.purchase_date, grams: String(g.grams), total_cost: String(g.total_cost), purity: g.purity || "" }); };
  const del = async (id: string) => { if (!confirm("Delete?")) return; await apiFetch(`/api/v1/gold/${id}`, { method: "DELETE" }); load(); };
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Gold Holdings</h2>
      <div className="card">
        <form onSubmit={submit} className="grid">
          <div><div className="label">Purchase date</div><input type="date" value={form.purchase_date} onChange={(e) => setForm({ ...form, purchase_date: e.target.value })} /></div>
          <div className="row">
            <div style={{ flex: 1 }}><div className="label">Grams</div><input value={form.grams} onChange={(e) => setForm({ ...form, grams: e.target.value })} placeholder="Grams" /></div>
            <div style={{ flex: 1 }}><div className="label">Total cost</div><input value={form.total_cost} onChange={(e) => setForm({ ...form, total_cost: e.target.value })} placeholder="Total cost" /></div>
          </div>
          <div><div className="label">Purity</div><input value={form.purity} onChange={(e) => setForm({ ...form, purity: e.target.value })} placeholder="Purity" /></div>
          <div className="row">
            <button type="submit">{editing ? "Update" : "Add"} holding</button>
            {editing && <button type="button" className="secondary" onClick={reset}>Cancel</button>}
          </div>
        </form>
      </div>
      <div className="card">
        <ul className="list">
          {items.map((g) => (
            <li key={g.id}>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <div>{g.purchase_date} · {g.grams}g · {g.total_cost}</div>
                <div className="row">
                  <button className="secondary" onClick={() => edit(g)}>Edit</button>
                  <button className="danger" onClick={() => del(g.id)}>Del</button>
                </div>
              </div>
            </li>
          ))}
          {items.length === 0 && <li>No gold holdings yet</li>}
        </ul>
      </div>
    </div>
  );
}
