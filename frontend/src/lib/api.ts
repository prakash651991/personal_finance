import { supabase } from "./supabase";

export async function apiFetch(path: string, options: RequestInit = {}) {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  let res: Response;
  try {
    res = await fetch(`${import.meta.env.VITE_API_BASE || "https://personal-finance-api-274092936620.asia-south1.run.app"}${path}`, {
      ...options,
      headers,
    });
  } catch {
    const msg = "Cannot reach the API server. Check your connection and try again.";
    (window as any).showToast?.(msg);
    throw new Error(msg);
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const msg = err?.detail || err?.error?.message || res.statusText || `HTTP ${res.status}`;
    (window as any).showToast?.("Failed: " + msg);
    throw new Error(msg);
  }
  const method = (options.method || "GET").toUpperCase();
  if (method !== "GET") {
    (window as any).showToast?.("Success");
  }
  return res.json();
}
