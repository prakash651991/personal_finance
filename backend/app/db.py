from supabase import create_client, Client
from .config import settings


def anon_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def user_client(access_token: str) -> Client:
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    client.postgrest.auth(access_token)
    return client


def service_client() -> Client | None:
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        return None
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
