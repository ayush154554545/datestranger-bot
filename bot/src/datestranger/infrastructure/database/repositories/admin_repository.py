from typing import Optional, Dict, Any, List
from ..client import get_supabase_client


class AdminRepository:
    def __init__(self, client=None):
        self._client = client or get_supabase_client()

    def log_admin_action(
        self,
        admin_user_id: str,
        action_type: str,
        target_user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        if not self._client or not admin_user_id or not action_type:
            return None
        try:
            payload = {
                "admin_user_id": admin_user_id,
                "action_type": action_type,
                "target_user_id": target_user_id,
                "metadata": metadata or {}
            }
            res = self._client.table("admin_actions").insert(payload).execute()
            return res.data[0] if res and res.data else None
        except Exception:
            return None

    def is_admin(self, user_id: str) -> bool:
        if not self._client or not user_id:
            return False
        try:
            res = self._client.table("admin_users").select("user_id").eq("user_id", user_id).execute()
            return bool(res and res.data)
        except Exception:
            return False

    def add_admin(
        self,
        user_id: str,
        role: str = "MODERATOR",
        permissions: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        if not self._client or not user_id:
            return None
        try:
            payload = {
                "user_id": user_id,
                "role": role,
                "permissions": permissions or []
            }
            res = self._client.table("admin_users").upsert(payload, on_conflict="user_id").execute()
            return res.data[0] if res and res.data else None
        except Exception:
            return None

    def remove_admin(self, user_id: str) -> bool:
        if not self._client or not user_id:
            return False
        try:
            res = self._client.table("admin_users").delete().eq("user_id", user_id).execute()
            return bool(res and res.data)
        except Exception:
            return False

