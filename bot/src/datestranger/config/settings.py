"""
Typed Application Settings Loader for DateWithStranger
"""

import os
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

env_file = os.getenv("ENV_FILE", ".env")
load_dotenv(dotenv_path=env_file, override=True)



@dataclass
class TelegramSettings:
    bot_token: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))
    admin_id: int = field(default_factory=lambda: int(os.getenv("ADMIN_ID", "0")))
    bot_name: str = field(default_factory=lambda: os.getenv("BOT_NAME", "DateWithStranger"))
    bot_user: str = field(default_factory=lambda: os.getenv("BOT_USER", "@testdate27_bot"))


@dataclass
class SupabaseSettings:
    url: str = field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    service_role_key: str = field(default_factory=lambda: os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""))
    anon_key: str = field(default_factory=lambda: os.getenv("SUPABASE_ANON_KEY", ""))


@dataclass
class RedisSettings:
    host: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    password: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_PASSWORD", None))
    db: int = field(default_factory=lambda: int(os.getenv("REDIS_DB", "0")))
    enabled: bool = field(default_factory=lambda: os.getenv("REDIS_ENABLED", "true").lower() == "true")


@dataclass
class R2Settings:
    account_id: str = field(default_factory=lambda: os.getenv("R2_ACCOUNT_ID", ""))
    access_key_id: str = field(default_factory=lambda: os.getenv("R2_ACCESS_KEY_ID", ""))
    secret_access_key: str = field(default_factory=lambda: os.getenv("R2_SECRET_ACCESS_KEY", ""))
    bucket_name: str = field(default_factory=lambda: os.getenv("R2_BUCKET_NAME", "datestranger-media"))


@dataclass
class CouchbaseSettings:
    endpoint: str = field(default_factory=lambda: os.getenv("COUCHBASE_ENDPOINT", ""))
    username: str = field(default_factory=lambda: os.getenv("COUCHBASE_USERNAME", ""))
    password: str = field(default_factory=lambda: os.getenv("COUCHBASE_PASSWORD", ""))
    bucket: str = field(default_factory=lambda: os.getenv("COUCHBASE_BUCKET", "lmedia"))
    scope: str = field(default_factory=lambda: os.getenv("COUCHBASE_SCOPE", "_default"))
    collection: str = field(default_factory=lambda: os.getenv("COUCHBASE_COLLECTION", "media"))


@dataclass
class DiscordSettings:
    status_webhook: Optional[str] = field(default_factory=lambda: os.getenv("STATUS_WEBHOOK"))
    alerts_webhook: Optional[str] = field(default_factory=lambda: os.getenv("ALERTS_WEBHOOK"))
    chat_log_webhook: Optional[str] = field(default_factory=lambda: os.getenv("CHAT_LOG_WEBHOOK"))
    media_log_webhook: Optional[str] = field(default_factory=lambda: os.getenv("MEDIA_LOG_WEBHOOK"))
    voice_log_webhook: Optional[str] = field(default_factory=lambda: os.getenv("VOICE_LOG_WEBHOOK"))
    girl_webhook: Optional[str] = field(default_factory=lambda: os.getenv("GIRL_WEBHOOK"))
    boy_webhook: Optional[str] = field(default_factory=lambda: os.getenv("BOY_WEBHOOK"))
    other_webhook: Optional[str] = field(default_factory=lambda: os.getenv("OTHER_WEBHOOK"))


@dataclass
class SecuritySettings:
    min_age: int = 18  # MANDATORY 18+ ADULT SERVICE GATE
    max_age: int = 80


@dataclass
class Settings:
    env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "true").lower() == "true")
    telegram: TelegramSettings = field(default_factory=TelegramSettings)
    supabase: SupabaseSettings = field(default_factory=SupabaseSettings)
    redis: RedisSettings = field(default_factory=RedisSettings)
    r2: R2Settings = field(default_factory=R2Settings)
    couchbase: CouchbaseSettings = field(default_factory=CouchbaseSettings)
    discord: DiscordSettings = field(default_factory=DiscordSettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)


_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
