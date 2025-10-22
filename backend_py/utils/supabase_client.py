from functools import lru_cache
from supabase import create_client, Client
from backend_py.config import get_settings


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    settings = get_settings()
    url = str(settings.supabase_url).rstrip("/") if settings.supabase_url else None
    service_role_key = settings.supabase_service_role_key
    anon_key = settings.supabase_anon_key
    key = service_role_key or anon_key

    if not url or not key:
        raise RuntimeError(
            "Missing or invalid Supabase configuration. Ensure SUPABASE_URL, and one of SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY are set in backend_py/.env or .env"
        )

    # Validate URL format (should be https://<ref>.supabase.co)
    if not (url.startswith("http://") or url.startswith("https://")):
        raise RuntimeError(
            "Invalid SUPABASE_URL. Expected the Supabase project URL like 'https://<ref>.supabase.co', not a database connection string."
        )

    return create_client(url, key)
