from datetime import datetime, timezone
from typing import Optional, Dict, Any
from ..client import get_supabase_client


class SystemSettingsRepository:
    def __init__(self, client=None):
        self._client = client or get_supabase_client()

    def get_setting(self, key: str) -> Optional[Any]:
        if not self._client or not key:
            return None
        try:
            res = self._client.table("system_settings").select("value").eq("key", key).execute()
            return res.data[0]["value"] if res and res.data else None
        except Exception:
            return None

    def set_setting(self, key: str, value: Any) -> bool:
        if not self._client or not key:
            return False
        try:
            now_iso = datetime.now(timezone.utc).isoformat()
            payload = {"key": key, "value": value, "updated_at": now_iso}
            res = self._client.table("system_settings").upsert(payload, on_conflict="key").execute()
            return bool(res and res.data)
        except Exception:
            return False

