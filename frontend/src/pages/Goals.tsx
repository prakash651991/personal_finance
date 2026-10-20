import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

export default function Goals() {
  const [goals, setGoals] = useState<any[]>([]);
  const [editing, setEditing] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", goal_type: "general", target_amount: "" });
  const load = () => apiFetch("/api/v1/savings-goals").then(setGoals).catch(console.error);
  useEffect(() => { load(); }, []);
  const reset = () => { setEditing(null); setForm({ name: "", goal_type: "general", target_amount: "" }); };
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const body = { ...form, target_amount: parseFloat(form.target_amount) };
    if (editing) await apiFetch(`/api/v1/savings-goals/${editing}`, { method: "PATCH", body: JSON.stringify(body) });
    else await apiFetch("/api/v1/savings-goals", { method: "POST", body: JSON.stringify(body) });
    reset(); load();
  };
  const edit = (g: any) => { setEditing(g.id); setForm({ name: g.name, goal_type: g.goal_type, target_amount: String(g.target_amount) }); };
  const del = async (id: string) => { if (!confirm("Delete?")) return; await apiFetch(`/api/v1/savings-goals/${id}`, { method: "DELETE" }); load(); };
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Savings Goals</h2>
      <div className="card">
        <form onSubmit={submit} className="grid">
          <div><div className="label">Goal name</div><input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Goal name" /></div>
          <div><div className="label">Target amount</div><input value={form.target_amount} onChange={(e) => setForm({ ...form, target_amount: e.target.value })} placeholder="Target amount" /></div>
          <div><div className="label">Goal type</div><select value={form.goal_type} onChange={(e) => setForm({ ...form, goal_type: e.target.value })}><option value="general">General</option><option value="emergency">Emergency</option><option value="gold">Gold</option><option value="home">Home</option><option value="vehicle">Vehicle</option><option value="education">Education</option><option value="travel">Travel</option></select></div>
          <div className="row">
            <button type="submit">{editing ? "Update" : "Add"} goal</button>
            {editing && <button type="button" className="secondary" onClick={reset}>Cancel</button>}
          </div>
        </form>
      </div>
      <div className="card">
        <ul className="list">
          {goals.map((g) => (
            <li key={g.id}>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <div>{g.name} · target {g.target_amount}</div>
                <div className="row">
                  <button className="secondary" onClick={() => edit(g)}>Edit</button>
                  <button className="danger" onClick={() => del(g.id)}>Del</button>
                </div>
              </div>
            </li>
          ))}
          {goals.length === 0 && <li>No goals yet</li>}
        </ul>
      </div>
    </div>
  );
}
