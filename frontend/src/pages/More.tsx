import { Link } from "react-router-dom";

const ITEMS = [
  ["/todo", "To-Do"],
  ["/profile", "Profile"],
  ["/accounts", "Accounts"],
  ["/categories", "Categories"],
  ["/credit-cards", "Credit Cards"],
  ["/recurring", "Recurring"],
  ["/goals", "Goals"],
];

export default function More() {
  return (
    <div>
      <h2>Settings</h2>
      <div className="grid grid2">
        {ITEMS.map(([p, l]) => (
          <Link key={p} to={p} className="card" style={{ textAlign: "center", fontWeight: 600 }}>
            {l}
          </Link>
        ))}
      </div>
    </div>
  );
}
