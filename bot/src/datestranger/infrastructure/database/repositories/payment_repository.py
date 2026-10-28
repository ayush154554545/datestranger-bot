from typing import Optional, Dict, Any
from ..client import get_supabase_client


class PaymentRepository:
    def __init__(self, client=None):
        self._client = client or get_supabase_client()

    def record_payment(self, user_id: str, provider_transaction_id: str, amount: float, currency: str = "XTR", payload: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        if not self._client:
            return None
        data = {
            "user_id": user_id,
            "provider_transaction_id": provider_transaction_id,
            "amount": amount,
            "currency": currency,
            "status": "completed",
            "payload": payload or {}
        }
        res = self._client.table("payment_transactions").insert(data).execute()
        return res.data[0] if res and res.data else None

    def get_payment_by_charge_id(self, charge_id: str) -> Optional[Dict[str, Any]]:
        if not self._client:
            return None
        res = self._client.table("payment_transactions").select("*").eq("provider_transaction_id", charge_id).execute()
        return res.data[0] if res and res.data else None
