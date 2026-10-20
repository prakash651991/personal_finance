import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

export default function Loans() {
  const [loans, setLoans] = useState<any[]>([]);
  const [editing, setEditing] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", start_date: new Date().toISOString().slice(0, 10), end_date: "", emi_amount: "", first_emi_date: "" });
  const [selected, setSelected] = useState<string | null>(null);
  const [insts, setInsts] = useState<any[]>([]);
  const load = () => apiFetch("/api/v1/loans").then(setLoans).catch(console.error);
  useEffect(() => { load(); }, []);
  const reset = () => { setEditing(null); setForm({ name: "", start_date: new Date().toISOString().slice(0, 10), end_date: "", emi_amount: "", first_emi_date: "" }); };
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const body: any = { ...form, emi_amount: parseFloat(form.emi_amount), end_date: form.end_date || form.start_date };
    if (editing) await apiFetch(`/api/v1/loans/${editing}`, { method: "PATCH", body: JSON.stringify(body) });
    else await apiFetch("/api/v1/loans", { method: "POST", body: JSON.stringify(body) });
    reset(); load();
  };
  const edit = (l: any) => { setEditing(l.id); setForm({ name: l.name, start_date: l.start_date, end_date: l.end_date || "", emi_amount: String(l.emi_amount), first_emi_date: l.first_emi_date || "" }); };
  const del = async (id: string) => { if (!confirm("Archive/delete?")) return; await apiFetch(`/api/v1/loans/${id}`, { method: "DELETE" }); load(); };
  const selectLoan = async (id: string) => {
    setSelected(id);
    setInsts(await apiFetch(`/api/v1/loans/${id}/installments`));
  };
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Loans</h2>
      <div className="card">
        <form onSubmit={submit} className="grid">
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Loan name" />
          <div className="row">
            <input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
            <input type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} placeholder="End date" />
          </div>
          <input value={form.emi_amount} onChange={(e) => setForm({ ...form, emi_amount: e.target.value })} placeholder="EMI amount" />
          <input type="date" value={form.first_emi_date} onChange={(e) => setForm({ ...form, first_emi_date: e.target.value })} />
          <div className="row">
            <button type="submit">{editing ? "Update" : "Add"} loan</button>
            {editing && <button type="button" className="secondary" onClick={reset}>Cancel</button>}
          </div>
        </form>
      </div>
      <div className="card">
        <ul className="list">
          {loans.map((l) => (
            <li key={l.id}>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <button className="secondary" style={{ flex: 1 }} onClick={() => selectLoan(l.id)}>{l.name} · EMI {l.emi_amount}</button>
                <button className="secondary" onClick={() => edit(l)}>Edit</button>
                <button className="danger" onClick={() => del(l.id)}>Del</button>
              </div>
            </li>
          ))}
          {loans.length === 0 && <li>No loans yet</li>}
        </ul>
      </div>
      {selected && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Installments</h3>
          <ul className="list">
            {insts.map((i) => <li key={i.id}>{i.installment_number}. {i.due_date} · {i.expected_amount} · {i.status} (paid {i.paid_amount})</li>)}
            {insts.length === 0 && <li>No installments</li>}
          </ul>
        </div>
      )}
    </div>
  );
}
