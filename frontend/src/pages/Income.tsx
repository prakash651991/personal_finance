import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

export default function Income() {
  const [sources, setSources] = useState<any[]>([]);
  const [editing, setEditing] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [type, setType] = useState("other");
  const load = () => apiFetch("/api/v1/income-sources").then(setSources).catch(console.error);
  useEffect(() => { load(); }, []);
  const reset = () => { setEditing(null); setName(""); setType("other"); };
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const body = { name, source_type: type };
    if (editing) await apiFetch(`/api/v1/income-sources/${editing}`, { method: "PATCH", body: JSON.stringify(body) });
    else await apiFetch("/api/v1/income-sources", { method: "POST", body: JSON.stringify(body) });
    reset(); load();
  };
  const edit = (s: any) => { setEditing(s.id); setName(s.name); setType(s.source_type); };
  const del = async (id: string) => { if (!confirm("Delete?")) return; await apiFetch(`/api/v1/income-sources/${id}`, { method: "DELETE" }); load(); };
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Income Sources</h2>
      <div className="card">
        <form onSubmit={submit} className="grid">
          <div><div className="label">Source name</div><input value={name} onChange={(e) => setName(e.target.value)} placeholder="Source name" /></div>
          <div><div className="label">Source type</div><select value={type} onChange={(e) => setType(e.target.value)}><option value="salary">Salary</option><option value="freelance">Freelance</option><option value="business">Business</option><option value="rent">Rent</option><option value="interest">Interest</option><option value="other">Other</option></select></div>
          <div className="row">
            <button type="submit">{editing ? "Update" : "Add"}</button>
            {editing && <button type="button" className="secondary" onClick={reset}>Cancel</button>}
          </div>
        </form>
      </div>
      <div className="card">
        <ul className="list">
          {sources.map((s) => (
            <li key={s.id}>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <div>{s.name} · {s.source_type}</div>
                <div className="row">
                  <button className="secondary" onClick={() => edit(s)}>Edit</button>
                  <button className="danger" onClick={() => del(s.id)}>Del</button>
                </div>
              </div>
            </li>
          ))}
          {sources.length === 0 && <li>No income sources yet</li>}
        </ul>
      </div>
    </div>
  );
}
