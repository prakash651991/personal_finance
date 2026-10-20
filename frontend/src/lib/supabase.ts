import { createClient } from "@supabase/supabase-js";

const url = import.meta.env.VITE_SUPABASE_URL || "https://fvdyrfmzujbfrmrjnajw.supabase.co";
const key = import.meta.env.VITE_SUPABASE_ANON_KEY || "sb_publishable_vOIYmCT4GevjBX2HRKO91A_9v6PVg-g";

export const supabase = createClient(url, key);
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
