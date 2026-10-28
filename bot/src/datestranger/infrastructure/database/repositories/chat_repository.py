from typing import Optional, Dict, Any, List
from ..client import get_supabase_client


class ChatRepository:
    def __init__(self, client=None):
        self._client = client or get_supabase_client()

    def log_message(self, chat_session_id: str, sender_id: str, recipient_id: str, message_type: str = "TEXT", text_content: Optional[str] = None, telegram_msg_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        if not self._client:
            return None
        payload = {
            "chat_session_id": chat_session_id,
            "sender_user_id": sender_id,
            "recipient_user_id": recipient_id,
            "message_type": message_type,
            "text_content": text_content,
            "telegram_message_id": telegram_msg_id
        }
        res = self._client.table("chat_messages").insert(payload).execute()
        return res.data[0] if res and res.data else None

    def get_session_history(self, chat_session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        if not self._client:
            return []
        res = self._client.table("chat_messages").select("*").eq("chat_session_id", chat_session_id).order("created_at", desc=True).limit(limit).execute()
        return res.data or []
