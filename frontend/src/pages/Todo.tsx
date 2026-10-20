import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../lib/api";

export default function Todo() {
  const [occs, setOccs] = useState<any[]>([]);
  const [recurring, setRecurring] = useState<any[]>([]);
  useEffect(() => {
    const cm = new Date().toISOString().slice(0, 7);
    apiFetch("/api/v1/recurring-expenses/occurrences").then((rows) => setOccs((rows || []).filter((r: any) => String(r.due_date).startsWith(cm)))).catch(console.error);
    apiFetch("/api/v1/recurring-expenses").then(setRecurring).catch(console.error);
  }, []);
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>To-Do (This Month)</h2>
      <div className="card">
        <ul className="list">
          {occs.map((o) => {
            const r = recurring.find((x) => x.id === o.recurring_expense_id);
            return (
              <li key={o.id}>
                <div className="row" style={{ justifyContent: "space-between" }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>{r ? r.name : "Recurring"}</div>
                    <div className="label">Due {o.due_date} · {o.expected_amount}</div>
                  </div>
                  <div className="row">
                    <span className="badge" style={{ background: o.status === "paid" ? "rgba(22,163,74,0.1)" : "rgba(220,38,38,0.1)", color: o.status === "paid" ? "var(--success)" : "var(--danger)" }}>
                      {o.status === "paid" ? "Paid" : "Unpaid"}
                    </span>
                    {o.status !== "paid" && <Link to={`/transactions?occ=${o.id}`}><button className="secondary">Pay</button></Link>}
                  </div>
                </div>
              </li>
            );
          })}
          {occs.length === 0 && <li>No recurring items this month</li>}
        </ul>
      </div>
    </div>
  );
}
