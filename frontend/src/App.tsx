import { useEffect, useState } from "react";
import { Routes, Route, Navigate, NavLink, useNavigate } from "react-router-dom";
import { supabase } from "./lib/supabase";
import Dashboard from "./pages/Dashboard";
import Accounts from "./pages/Accounts";
import Transactions from "./pages/Transactions";
import CreditCards from "./pages/CreditCards";
import Budgets from "./pages/Budgets";
import Goals from "./pages/Goals";
import Gold from "./pages/Gold";
import Recurring from "./pages/Recurring";
import Income from "./pages/Income";
import Reports from "./pages/Reports";
import Profile from "./pages/Profile";
import More from "./pages/More";
import Todo from "./pages/Todo";
import Categories from "./pages/Categories";

const NAV = [
  ["/", "Home", "M3 12l9-9 9 9M5 10v10h14V10"],
  ["/transactions", "Txns", "M4 6h16M4 12h16M4 18h16"],
  ["/more", "Setting", "M4 6h16M4 12h16M4 18h16"],
  ["/reports", "Reports", "M4 19V5M10 19V9M16 19v-6M22 19V3"],
  ["/profile", "Profile", "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 20a8 8 0 0 1 16 0"],
];

function Auth() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [msg, setMsg] = useState("");
  const navigate = useNavigate();
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (mode === "signin") {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) setMsg(error.message);
      else navigate("/");
    } else {
      const { error } = await supabase.auth.signUp({ email, password });
      if (error) setMsg(error.message);
      else setMsg("Check email for confirmation");
    }
  };
  return (
    <div className="authwrap">
      <div className="card authcard">
        <h2 style={{ marginTop: 0 }}>{mode === "signin" ? "Welcome back" : "Create account"}</h2>
        <form onSubmit={submit} className="grid">
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
          <button type="submit">{mode === "signin" ? "Sign in" : "Sign up"}</button>
        </form>
        <button className="secondary mt8" style={{ width: "100%" }} onClick={() => setMode(mode === "signin" ? "signup" : "signin")}>
          {mode === "signin" ? "Need account? Sign up" : "Have account? Sign in"}
        </button>
        {msg && <p style={{ color: "var(--danger)" }}>{msg}</p>}
      </div>
    </div>
  );
}

export default function App() {
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState("");
  useEffect(() => {
    (window as any).showToast = (m: string) => {
      setToast(m);
      setTimeout(() => setToast(""), 2500);
    };
  }, []);
  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setLoading(false);
    });
    const { data: sub } = supabase.auth.onAuthStateChange((_e, s) => setSession(s));
    return () => sub.subscription.unsubscribe();
  }, []);
  if (loading) return <div className="authwrap">Loading...</div>;
  if (!session) {
    return (
      <Routes>
        <Route path="*" element={<Auth />} />
      </Routes>
    );
  }
  return (
    <>
      <div className="appbar">Personal Finance</div>
      <div className="content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/accounts" element={<Accounts />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/income" element={<Income />} />
          <Route path="/credit-cards" element={<CreditCards />} />
          <Route path="/budgets" element={<Budgets />} />
          <Route path="/recurring" element={<Recurring />} />
          <Route path="/goals" element={<Goals />} />
          <Route path="/gold" element={<Gold />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/more" element={<More />} />
          <Route path="/todo" element={<Todo />} />
          <Route path="/categories" element={<Categories />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
      {toast && <div className="toast">{toast}</div>}
      <nav className="bottomnav">
        {NAV.map(([p, l, icon]) => (
          <NavLink key={p} to={p} className={({ isActive }) => (isActive ? "active" : "")}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d={icon} />
            </svg>
            {l}
          </NavLink>
        ))}
      </nav>
    </>
  );
}
