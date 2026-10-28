import os
from typing import Optional

try:
    from supabase import create_client, Client
except ImportError:
    Client = None
    create_client = None


class SupabaseDatabaseClient:
    """
    Centralized Supabase Database Client Manager.
    Enforces singleton pattern and secure service-role key usage on the server.
    """
    _instance: Optional['SupabaseDatabaseClient'] = None
    _client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseDatabaseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        url: str = os.getenv("SUPABASE_URL", "")
        service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

        if url and service_role_key and create_client:
            try:
                self._client = create_client(url, service_role_key)
            except Exception as e:
                print(f"[SUPABASE CLIENT WARNING] Initialization failed: {e}")
                self._client = None
        else:
            self._client = None

    @property
    def client(self) -> Optional[Client]:
        return self._client

    def is_connected(self) -> bool:
        return self._client is not None


def get_supabase_client() -> Optional[Client]:
    """Helper accessor for the Supabase client instance."""
    return SupabaseDatabaseClient().client
