from typing import Optional, Dict, Any, List
from ..client import get_supabase_client


class ReportRepository:
    def __init__(self, client=None):
        self._client = client or get_supabase_client()

    def create_report(self, reporter_id: str, reported_id: str, reason: str, description: Optional[str] = None, match_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self._client:
            return None
        payload = {
            "reporter_user_id": reporter_id,
            "reported_user_id": reported_id,
            "match_id": match_id,
            "reason": reason,
            "description": description,
            "status": "pending"
        }
        res = self._client.table("reports").insert(payload).execute()
        return res.data[0] if res and res.data else None

    def get_pending_reports(self, limit: int = 20) -> List[Dict[str, Any]]:
        if not self._client:
            return []
        res = self._client.table("reports").select("*").eq("status", "pending").order("created_at", desc=True).limit(limit).execute()
        return res.data or []
