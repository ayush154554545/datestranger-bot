from typing import Optional, Dict, Any
from ..client import get_supabase_client


class MediaRepository:
    def __init__(self, client=None):
        self._client = client or get_supabase_client()

    def register_media(self, owner_user_id: str, storage_provider: str = "telegram", storage_key: Optional[str] = None, mime_type: str = "image/jpeg", file_size: Optional[int] = None) -> Optional[Dict[str, Any]]:
        if not self._client:
            return None
        payload = {
            "owner_user_id": owner_user_id,
            "storage_provider": storage_provider,
            "storage_key": storage_key,
            "mime_type": mime_type,
            "file_size": file_size,
            "processing_status": "ready"
        }
        res = self._client.table("media").insert(payload).execute()
        return res.data[0] if res and res.data else None
