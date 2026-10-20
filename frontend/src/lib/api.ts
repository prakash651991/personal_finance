import { supabase } from "./supabase";

export async function apiFetch(path: string, options: RequestInit = {}) {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(`${import.meta.env.VITE_API_BASE || "http://localhost:8000"}${path}`, {
    ...options,
    headers,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const msg = err?.error?.message || res.statusText;
    (window as any).showToast?.("Failed: " + msg);
    throw new Error(msg);
  }
  const method = (options.method || "GET").toUpperCase();
  if (method !== "GET") {
    (window as any).showToast?.("Success");
  }
  return res.json();
}
