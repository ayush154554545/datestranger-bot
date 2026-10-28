from datetime import datetime, timezone
from typing import Optional, Dict, Any
from ..client import get_supabase_client


class UserRepository:
    def __init__(self, client=None):
        self._client = client or get_supabase_client()

    def get_by_telegram_id(self, telegram_user_id: int) -> Optional[Dict[str, Any]]:
        if not self._client or not telegram_user_id:
            return None
        try:
            res = self._client.table("users").select("*").eq("telegram_user_id", telegram_user_id).execute()
            return res.data[0] if res and res.data else None
        except Exception:
            return None

    def create_user(
        self,
        telegram_user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        if not self._client or not telegram_user_id:
            return None
        try:
            payload = {
                "telegram_user_id": telegram_user_id,
                "telegram_username": username,
                "first_name": first_name,
                "last_name": last_name,
                "account_status": "active",
                "eligibility_status": "unverified"
            }
            res = self._client.table("users").upsert(payload, on_conflict="telegram_user_id").execute()
            return res.data[0] if res and res.data else None
        except Exception:
            return None

    def update_last_seen(self, telegram_user_id: int) -> bool:
        if not self._client or not telegram_user_id:
            return False
        try:
            now_iso = datetime.now(timezone.utc).isoformat()
            res = self._client.table("users").update({"last_seen_at": now_iso}).eq("telegram_user_id", telegram_user_id).execute()
            return bool(res and res.data)
        except Exception:
            return False

