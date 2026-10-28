from typing import Optional, Dict, Any
from ..client import get_supabase_client


class PremiumRepository:
    def __init__(self, client=None):
        self._client = client or get_supabase_client()

    def get_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        if not self._client:
            return None
        res = self._client.table("premium_subscriptions").select("*").eq("user_id", user_id).eq("status", "active").execute()
        return res.data[0] if res and res.data else None

    def grant_premium(self, user_id: str, days: int, plan_id: Optional[str] = None) -> bool:
        if not self._client:
            return False
        res = self._client.rpc("grant_premium_subscription", {"p_user_id": user_id, "p_days": days, "p_plan_id": plan_id}).execute()
        return True
