from typing import Optional, Dict, Any
from ..client import get_supabase_client


class ReferralRepository:
    def __init__(self, client=None):
        self._client = client or get_supabase_client()

    def process_referral(self, referrer_id: str, referred_id: str) -> Optional[Dict[str, Any]]:
        if referrer_id == referred_id:
            raise ValueError("Self referral is strictly prohibited.")
        if not self._client:
            return None
        payload = {
            "referrer_user_id": referrer_id,
            "referred_user_id": referred_id
        }
        res = self._client.table("referrals").insert(payload).execute()
        return res.data[0] if res and res.data else None

    def get_referral_count(self, referrer_id: str) -> int:
        if not self._client:
            return 0
        res = self._client.table("referrals").select("id", count="exact").eq("referrer_user_id", referrer_id).execute()
        return res.count or 0
