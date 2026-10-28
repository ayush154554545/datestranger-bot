from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from ..client import get_supabase_client


class MatchRepository:
    def __init__(self, client=None):
        self._client = client or get_supabase_client()

    def get_active_match_for_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        if not self._client or not user_id:
            return None
        try:
            res = self._client.table("match_participants").select("match_id, matches(*)").eq("user_id", user_id).eq("status", "active").execute()
            return res.data[0] if res and res.data else None
        except Exception:
            return None

    def create_atomic_match(self, user1_id: str, user2_id: str) -> Optional[Dict[str, Any]]:
        """
        Executes stored function create_atomic_match ensuring concurrency safety
        and race-condition resistance.
        """
        if not self._client or not user1_id or not user2_id:
            return None
        res = self._client.rpc("create_atomic_match", {"p_user1_id": user1_id, "p_user2_id": user2_id}).execute()
        return res.data[0] if res and res.data else None

    def end_match(self, match_id: str, ended_reason: str = "user_left") -> bool:
        if not self._client or not match_id:
            return False
        try:
            now_iso = datetime.now(timezone.utc).isoformat()
            # Update match status
            self._client.table("matches").update({"status": "ended", "ended_at": now_iso, "ended_reason": ended_reason}).eq("id", match_id).execute()
            # Update participants
            self._client.table("match_participants").update({"status": "left", "left_at": now_iso}).eq("match_id", match_id).execute()
            return True
        except Exception:
            return False

