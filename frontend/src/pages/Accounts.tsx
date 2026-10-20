import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

export default function Accounts() {
  const [accounts, setAccounts] = useState<any[]>([]);
  const [editing, setEditing] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [type, setType] = useState("bank");
  const [opening, setOpening] = useState("0");
  const load = () => apiFetch("/api/v1/accounts").then((rows) => setAccounts((rows || []).filter((a: any) => a.is_active !== false))).catch(console.error);
  useEffect(() => { load(); }, []);
  const reset = () => { setEditing(null); setName(""); setType("bank"); setOpening("0"); };
  const toast = (m: string) => (window as any).showToast?.(m);
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const body = { name, account_type: type, opening_balance: parseFloat(opening) };
      if (editing) await apiFetch(`/api/v1/accounts/${editing}`, { method: "PATCH", body: JSON.stringify(body) });
      else await apiFetch("/api/v1/accounts", { method: "POST", body: JSON.stringify(body) });
      toast(editing ? "Account updated" : "Account added");
      reset(); load();
    } catch (e: any) { toast("Failed: " + (e?.message || "error")); }
  };
  const edit = (a: any) => { setEditing(a.id); setName(a.name); setType(a.account_type); setOpening(String(a.opening_balance)); };
  const del = async (id: string) => {
    if (!confirm("Delete?")) return;
    try { await apiFetch(`/api/v1/accounts/${id}`, { method: "DELETE" }); toast("Account deleted"); load(); }
    catch (e: any) { toast("Failed: " + (e?.message || "error")); }
  };
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Accounts</h2>
      <div className="card">
        <form onSubmit={submit} className="grid">
          <div><div className="label">Account name</div><input value={name} onChange={(e) => setName(e.target.value)} placeholder="Account name" /></div>
          <div><div className="label">Account type</div><select value={type} onChange={(e) => setType(e.target.value)}><option value="bank">Bank</option><option value="cash">Cash</option><option value="savings">Savings</option><option value="other">Other</option></select></div>
          <div><div className="label">Opening balance</div><input value={opening} onChange={(e) => setOpening(e.target.value)} placeholder="Opening balance" /></div>
          <div className="row">
            <button type="submit">{editing ? "Update" : "Add"} account</button>
            {editing && <button type="button" className="secondary" onClick={reset}>Cancel</button>}
          </div>
        </form>
      </div>
      <div className="card">
        <ul className="list">
          {accounts.map((a) => (
            <li key={a.id}>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <div>
                  <div style={{ fontWeight: 600 }}>{a.name}</div>
                  <div className="label">{a.account_type} · {a.opening_balance}</div>
                </div>
                <div className="row">
                  <button className="secondary" onClick={() => edit(a)}>Edit</button>
                  <button className="danger" onClick={() => del(a.id)}>Del</button>
                </div>
              </div>
            </li>
          ))}
          {accounts.length === 0 && <li>No accounts yet</li>}
        </ul>
      </div>
    </div>
  );
}
