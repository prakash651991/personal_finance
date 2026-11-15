"""
One-shot provisioning for a fresh Supabase project.

Applies the schema, seeds system categories, (optionally) creates a confirmed
login user, and writes the local env files.

Usage (pooler connection string recommended, works over IPv4):

    python scripts/provision_supabase.py ^
        --ref <project-ref> ^
        --db-url "postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres" ^
        --url https://<ref>.supabase.co ^
        --anon-key <publishable-anon-key> ^
        --service-role <service-role-key> ^
        --email you@example.com --password "Secret123!"

Then redeploy:

    gcloud run deploy personal-finance-api --source backend ...
    cd frontend; vercel --prod --yes
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.request

import psycopg2

ROOT = pathlib.Path(__file__).resolve().parent.parent
MIGRATION = ROOT / "supabase" / "migrations" / "0001_initial.sql"
SEED = ROOT / "supabase" / "seed.sql"

# Errors that simply mean "already applied".
IDEMPOTENT_CODES = {
    "42P07",  # duplicate_table
    "42710",  # duplicate_object (policy/extension/trigger)
    "42723",  # duplicate_function
    "42P06",  # duplicate_schema
    "42P16",  # invalid_table_definition (index exists)
    "23505",  # unique_violation (seeded rows)
}


def split_statements(sql: str) -> list[str]:
    """Split SQL on semicolons, ignoring ones inside string literals."""
    statements: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    for ch in sql:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            buf.append(ch)
            continue
        if ch == ";":
            chunk = "".join(buf).strip()
            if chunk:
                statements.append(chunk)
            buf = []
            continue
        buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)
    return statements


def run_sql_file(cur, path: pathlib.Path) -> None:
    sql = path.read_text(encoding="utf-8")
    try:
        cur.execute(sql)
        print(f"  applied {path.name}")
        return
    except Exception as exc:  # noqa: BLE001
        if getattr(exc, "pgcode", None) not in IDEMPOTENT_CODES:
            # Replay statement by statement so one existing object does not
            # abort the rest of the migration.
            print(f"  {path.name}: batched run stopped ({exc.__class__.__name__}), replaying per statement")

    applied = skipped = 0
    for statement in split_statements(sql):
        try:
            cur.execute(statement)
            applied += 1
        except Exception as exc:  # noqa: BLE001
            if getattr(exc, "pgcode", None) in IDEMPOTENT_CODES:
                skipped += 1
                continue
            raise
    print(f"  applied {path.name} ({applied} statements, {skipped} already present)")


def apply_sql(db_url: str) -> None:
    print("Applying schema...")
    conn = psycopg2.connect(db_url, connect_timeout=20)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for file in (MIGRATION, SEED):
                if file.exists():
                    run_sql_file(cur, file)
    finally:
        conn.close()


def create_user(base_url: str, service_role: str, email: str, password: str) -> str | None:
    """Create (or update) a confirmed auth user. Returns the user id."""
    body = json.dumps({"email": email, "password": password, "email_confirm": True}).encode()
    req = urllib.request.Request(
        f"{base_url}/auth/v1/admin/users",
        data=body,
        method="POST",
        headers={
            "apikey": service_role,
            "Authorization": f"Bearer {service_role}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read())
            print(f"  created user {email}")
            return payload.get("id")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        if exc.code in (400, 409, 422) and "already" in detail.lower():
            print(f"  user {email} already exists")
            return None
        print(f"  user creation failed ({exc.code}): {detail}")
        return None


def ensure_profile(db_url: str, user_id: str | None, email: str) -> None:
    if not user_id:
        return
    conn = psycopg2.connect(db_url, connect_timeout=20)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into public.profiles (id, display_name)
                values (%s, %s)
                on conflict (id) do nothing
                """,
                (user_id, email.split("@")[0]),
            )
        print("  profile row ensured")
    finally:
        conn.close()


def write_env(api_url: str, anon_key: str) -> None:
    backend_env = ROOT / "backend" / ".env"
    frontend_env = ROOT / "frontend" / ".env"

    lines = []
    if backend_env.exists():
        for line in backend_env.read_text(encoding="utf-8").splitlines():
            if line.startswith(("SUPABASE_URL=", "SUPABASE_ANON_KEY=")):
                continue
            lines.append(line)
    lines = [f"SUPABASE_URL={api_url}", f"SUPABASE_ANON_KEY={anon_key}"] + lines
    backend_env.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

    frontend_env.write_text(
        f"VITE_SUPABASE_URL={api_url}\n"
        f"VITE_SUPABASE_ANON_KEY={anon_key}\n"
        f"VITE_API_BASE=https://personal-finance-api-274092936620.asia-south1.run.app\n",
        encoding="utf-8",
    )
    print("  wrote backend/.env and frontend/.env")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-url", required=True, help="Postgres connection string")
    parser.add_argument("--url", required=True, help="https://<ref>.supabase.co")
    parser.add_argument("--anon-key", required=True)
    parser.add_argument("--service-role", default="")
    parser.add_argument("--email", default="")
    parser.add_argument("--password", default="")
    args = parser.parse_args()

    try:
        apply_sql(args.db_url)
        if args.service_role and args.email and args.password:
            user_id = create_user(args.url, args.service_role, args.email, args.password)
            ensure_profile(args.db_url, user_id, args.email)
        write_env(args.url.rstrip("/"), args.anon_key)
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1

    print("\nDone. Redeploy the backend and frontend with the new credentials.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
