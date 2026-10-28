from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from ..client import get_supabase_client


class BanRepository:
    def __init__(self, client=None):
        self._client = client or get_supabase_client()

    def ban_user(
        self,
        user_id: str,
        reason: str,
        ban_type: str = "permanent",
        created_by_admin_id: Optional[str] = None,
        duration_days: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        if not self._client or not user_id or not reason:
            return None
        try:
            expires_at = None
            if duration_days:
                now = datetime.now(timezone.utc)
                expires_at = (now + timedelta(days=duration_days)).isoformat()

            payload = {
                "user_id": user_id,
                "ban_type": ban_type,
                "reason": reason,
                "created_by_user_id": created_by_admin_id,
                "expires_at": expires_at
            }
            res = self._client.table("bans").insert(payload).execute()
            return res.data[0] if res and res.data else None
        except Exception:
            return None

    def is_user_banned(self, user_id: str) -> bool:
        if not self._client or not user_id:
            return False
        try:
            res = self._client.table("bans").select("*").eq("user_id", user_id).execute()
            if not res or not res.data:
                return False

            now = datetime.now(timezone.utc)
            for ban in res.data:
                expires_at_str = ban.get("expires_at")
                if not expires_at_str:
                    return True  # Permanent ban

                try:
                    expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
                    if expires_at.tzinfo is None:
                        expires_at = expires_at.replace(tzinfo=timezone.utc)
                    if expires_at > now:
                        return True  # Active temporary ban
                except Exception:
                    return True

            return False
        except Exception:
            return False

    def unban_user(self, user_id: str) -> bool:
        if not self._client or not user_id:
            return False
        try:
            res = self._client.table("bans").delete().eq("user_id", user_id).execute()
            return bool(res and res.data)
        except Exception:
            return False

