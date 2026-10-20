import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../lib/api";

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    apiFetch("/api/v1/dashboard/summary").then(setData).catch(console.error);
  }, []);
  if (!data) return <div className="card">Loading...</div>;
  return (
    <div>
      <div className="card" style={{ background: "linear-gradient(135deg, var(--accent), var(--accent-2))", color: "#fff", border: "none" }}>
        <div className="label" style={{ color: "rgba(255,255,255,0.7)" }}>Net cash flow</div>
        <div style={{ fontSize: "var(--step-4)", fontWeight: 800, letterSpacing: "-0.03em" }}>{data.net_cash_flow}</div>
        <div className="row" style={{ marginTop: "var(--space-m)" }}>
          <div style={{ flex: 1 }}>
            <div className="label" style={{ color: "rgba(255,255,255,0.7)" }}>Income</div>
            <div style={{ fontWeight: 700 }}>{data.income}</div>
          </div>
          <div style={{ flex: 1 }}>
            <div className="label" style={{ color: "rgba(255,255,255,0.7)" }}>Expense</div>
            <div style={{ fontWeight: 700 }}>{data.expense}</div>
          </div>
          <div style={{ flex: 1 }}>
            <div className="label" style={{ color: "rgba(255,255,255,0.7)" }}>Balance</div>
            <div style={{ fontWeight: 700 }}>{data.total_balance}</div>
          </div>
        </div>
      </div>

      <div className="grid grid2">
        <div className="card flat">
          <div className="label">Card liability</div>
          <div className="stat">{data.card_liability}</div>
        </div>
        <div className="card flat">
          <div className="label">Monthly EMI</div>
          <div className="stat">{data.total_monthly_emi}</div>
        </div>
        <div className="card flat">
          <div className="label">Budget left</div>
          <div className="stat">{data.budget_remaining}</div>
        </div>
        <Link to="/transactions" className="card flat" style={{ display: "block" }}>
          <div className="label">Quick add</div>
          <div className="stat" style={{ fontSize: "var(--step-2)" }}>+ Transaction</div>
        </Link>
      </div>

      <div className="card">
        <h3>Goals</h3>
        <ul className="list">
          {(data.goals || []).map((g: any) => (
            <li key={g.goal_id}>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <div style={{ fontWeight: 600 }}>{g.name}</div>
                <div className="stat" style={{ fontSize: "var(--step-1)" }}>{g.balance} / {g.target}</div>
              </div>
            </li>
          ))}
          {(!data.goals || data.goals.length === 0) && <li>No goals yet</li>}
        </ul>
      </div>
    </div>
  );
}
