import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

export default function Categories() {
  const [items, setItems] = useState<any[]>([]);
  const [editing, setEditing] = useState<string | null>(null);
  const [name, setName] = useState("");
  const load = () => apiFetch("/api/v1/categories").then(setItems).catch(console.error);
  useEffect(() => { load(); }, []);
  const reset = () => { setEditing(null); setName(""); };
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (editing) await apiFetch(`/api/v1/categories/${editing}`, { method: "PATCH", body: JSON.stringify({ name }) });
    else await apiFetch("/api/v1/categories", { method: "POST", body: JSON.stringify({ name }) });
    reset(); load();
  };
  const edit = (c: any) => { setEditing(c.id); setName(c.name); };
  const del = async (id: string) => { if (!confirm("Delete category?")) return; await apiFetch(`/api/v1/categories/${id}`, { method: "DELETE" }); load(); };
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Categories</h2>
      <div className="card">
        <form onSubmit={submit} className="row">
          <div style={{ flex: 1 }}><div className="label">Category name</div><input value={name} onChange={(e) => setName(e.target.value)} placeholder="Category name" /></div>
          <button type="submit">{editing ? "Update" : "Add"}</button>
          {editing && <button type="button" className="secondary" onClick={reset}>Cancel</button>}
        </form>
      </div>
      <div className="card">
        <ul className="list">
          {items.map((c) => (
            <li key={c.id}>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <div>{c.name} {c.is_system ? "(system)" : ""}</div>
                <div className="row">
                  <button className="secondary" onClick={() => edit(c)}>Edit</button>
                  <button className="danger" onClick={() => del(c.id)}>Del</button>
                </div>
              </div>
            </li>
          ))}
          {items.length === 0 && <li>No categories yet</li>}
        </ul>
      </div>
    </div>
  );
}
