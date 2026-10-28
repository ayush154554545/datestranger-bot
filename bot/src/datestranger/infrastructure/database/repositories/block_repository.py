from typing import Optional, Dict, Any, List
from ..client import get_supabase_client


class BlockRepository:
    def __init__(self, client=None):
        self._client = client or get_supabase_client()

    def block_user(self, blocker_id: str, blocked_id: str) -> bool:
        if blocker_id == blocked_id:
            raise ValueError("Self blocking is not allowed.")
        if not self._client or not blocker_id or not blocked_id:
            return False
        try:
            payload = {"blocker_user_id": blocker_id, "blocked_user_id": blocked_id}
            res = self._client.table("blocks").upsert(payload, on_conflict="blocker_user_id, blocked_user_id").execute()
            return bool(res and res.data)
        except Exception:
            return False

    def unblock_user(self, blocker_id: str, blocked_id: str) -> bool:
        if not self._client or not blocker_id or not blocked_id:
            return False
        try:
            res = self._client.table("blocks").delete().eq("blocker_user_id", blocker_id).eq("blocked_user_id", blocked_id).execute()
            return bool(res and res.data)
        except Exception:
            return False

    def is_blocked(self, blocker_id: str, blocked_id: str) -> bool:
        if not self._client or not blocker_id or not blocked_id:
            return False
        try:
            res = self._client.table("blocks").select("blocker_user_id").eq("blocker_user_id", blocker_id).eq("blocked_user_id", blocked_id).execute()
            return bool(res and res.data)
        except Exception:
            return False

