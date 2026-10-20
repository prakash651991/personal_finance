import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { supabase } from "../lib/supabase";

export default function Profile() {
  const [user, setUser] = useState<any>(null);
  const [name, setName] = useState("");
  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setUser(data.user));
    apiFetch("/api/v1/profile").then((p) => { setName(p?.display_name || ""); }).catch(console.error);
  }, []);
  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    await apiFetch("/api/v1/profile", { method: "PATCH", body: JSON.stringify({ display_name: name }) });
    (window as any).showToast?.("Profile updated");
  };
  const logout = async () => { await supabase.auth.signOut(); };
  const initial = (user?.email || "?").charAt(0).toUpperCase();
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Profile</h2>
      <div className="card" style={{ textAlign: "center" }}>
        <div style={{ width: 72, height: 72, borderRadius: "50%", background: "var(--accent)", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28, fontWeight: 700, margin: "0 auto var(--space-m)" }}>
          {initial}
        </div>
        <div style={{ fontWeight: 600 }}>{user?.email}</div>
        <div className="label">User ID: {user?.id}</div>
      </div>
      <div className="card">
        <form onSubmit={save} className="grid">
          <div><div className="label">Display name</div><input value={name} onChange={(e) => setName(e.target.value)} placeholder="Display name" /></div>
          <button type="submit">Save profile</button>
        </form>
      </div>
      <div className="card">
        <button className="danger" style={{ width: "100%" }} onClick={logout}>Log out</button>
      </div>
    </div>
  );
}
