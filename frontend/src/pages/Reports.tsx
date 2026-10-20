import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { supabase } from "../lib/supabase";

export default function Reports() {
  const [cf, setCf] = useState<any>(null);
  const [sp, setSp] = useState<any>(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    Promise.all([
      apiFetch("/api/v1/reports/cash-flow").then(setCf),
      apiFetch("/api/v1/reports/spending").then(setSp),
    ]).catch((e) => setErr(String(e))).finally(() => setLoading(false));
  }, []);
  if (loading) return <div className="card">Loading reports...</div>;
  if (err) return <div className="card" style={{ color: "var(--danger)" }}>{err}</div>;
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Reports</h2>
      <div className="card">
        <h3 style={{ marginTop: 0 }}>Cash Flow (monthly)</h3>
        <ul className="list">
          {Object.entries(cf?.monthly || {}).map(([m, v]: any) => (
            <li key={m}>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <div style={{ fontWeight: 600 }}>{m}</div>
                <div>Income {v.income} · Expense {v.expense}</div>
              </div>
            </li>
          ))}
          {Object.keys(cf?.monthly || {}).length === 0 && <li>No data</li>}
        </ul>
      </div>
      <div className="card">
        <h3 style={{ marginTop: 0 }}>Spending by Category</h3>
        <ul className="list">
          {Object.entries(sp?.by_category || {}).map(([k, v]: any) => (
            <li key={k}>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <div>{k}</div>
                <div className="stat" style={{ fontSize: "var(--step-1)" }}>{v}</div>
              </div>
            </li>
          ))}
          {Object.keys(sp?.by_category || {}).length === 0 && <li>No spending data</li>}
        </ul>
      </div>
      <div className="card">
        <button type="button" onClick={async () => {
          const { data } = await supabase.auth.getSession();
          const token = data.session?.access_token;
          const res = await fetch(`${import.meta.env.VITE_API_BASE || "http://localhost:8000"}/api/v1/exports/transactions`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
          const blob = await res.blob();
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "transactions.csv";
          a.click();
          URL.revokeObjectURL(url);
        }}>Export transactions CSV</button>
      </div>
    </div>
  );
}
