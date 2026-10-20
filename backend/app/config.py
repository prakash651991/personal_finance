from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    SUPABASE_URL: str = "https://fvdyrfmzujbfrmrjnajw.supabase.co"
    SUPABASE_ANON_KEY: str = "sb_publishable_vOIYmCT4GevjBX2HRKO91A_9v6PVg-g"
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    APP_ENV: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"


settings = Settings()
