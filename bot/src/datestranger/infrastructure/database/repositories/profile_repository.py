from typing import Optional, Dict, Any
from ..client import get_supabase_client


class ProfileRepository:
    def __init__(self, client=None):
        self._client = client or get_supabase_client()

    def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        if not self._client:
            return None
        res = self._client.table("profiles").select("*").eq("user_id", user_id).execute()
        return res.data[0] if res and res.data else None

    def upsert_profile(self, user_id: str, display_name: str, age: int, gender: str, country: str = "any", language: str = "en", bio: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if age < 18:
            raise ValueError("Age eligibility violation: DateWithStranger strictly requires 18+")
        if not self._client:
            return None
        payload = {
            "user_id": user_id,
            "display_name": display_name,
            "age": age,
            "gender": gender,
            "country": country,
            "language": language,
            "bio": bio,
            "profile_status": "complete"
        }
        res = self._client.table("profiles").upsert(payload, on_conflict="user_id").execute()
        return res.data[0] if res and res.data else None
