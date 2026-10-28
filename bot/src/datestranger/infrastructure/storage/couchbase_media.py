"""Couchbase Capella media storage.

Stores small media bytes (photos, voice notes) as documents in a Couchbase
collection so the project does not depend on Cloudflare R2. Large files stay
on the ``telegram`` provider (Telegram file_ids), because Couchbase has a
~20 MB per-document limit and no CDN/public-URL semantics.

Document shape (key ``media::<media_id>``)::

    {"mime": ..., "size": ..., "owner": ..., "sha256": ...,
     "created_at": ..., "data_b64": ...}

Register the returned key in Postgres ``media.storage_key`` with
``storage_provider = 'couchbase'`` (see migration 009).
"""

import base64
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

MAX_DOC_BYTES = 20 * 1024 * 1024  # Couchbase hard per-document limit


class CouchbaseMediaStore:
    """Thin KV wrapper around one Couchbase collection. Connects lazily."""

    def __init__(
        self,
        endpoint: str,
        username: str,
        password: str,
        bucket: str = "lmedia",
        scope: str = "_default",
        collection: str = "media",
    ) -> None:
        if not endpoint or not username or not password:
            raise ValueError("Couchbase endpoint/username/password are all required")
        self._endpoint = endpoint
        self._username = username
        self._password = password
        self._bucket_name = bucket
        self._scope_name = scope
        self._collection_name = collection
        self._collection = None

    def _get_collection(self):
        if self._collection is not None:
            return self._collection
        try:
            from couchbase.auth import PasswordAuthenticator
            from couchbase.cluster import Cluster
            from couchbase.options import ClusterOptions
        except ImportError as exc:
            raise RuntimeError(
                "couchbase package not installed; run: pip install -r bot/requirements.txt"
            ) from exc
        auth = PasswordAuthenticator(self._username, self._password)
        options = ClusterOptions(auth)
        options.apply_profile("wan_development")  # Capella WAN latency profile
        cluster = Cluster(self._endpoint, options)
        cluster.wait_until_ready(timedelta(seconds=10))
        bucket = cluster.bucket(self._bucket_name)
        scope = bucket.scope(self._scope_name)
        self._collection = scope.collection(self._collection_name)
        return self._collection

    @staticmethod
    def _key(media_id: str) -> str:
        return f"media::{media_id}"

    def save(self, data: bytes, mime_type: str, owner: str = "") -> str:
        """Persist bytes, return the media_id (storage_key). Raises on oversize."""
        if not data:
            raise ValueError("empty media payload")
        if len(data) > MAX_DOC_BYTES:
            raise ValueError(
                f"media {len(data)} bytes exceeds Couchbase document limit; "
                "use the 'telegram' provider for large files"
            )
        media_id = uuid.uuid4().hex
        doc: Dict[str, Any] = {
            "mime": mime_type,
            "size": len(data),
            "owner": owner,
            "sha256": hashlib.sha256(data).hexdigest(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "data_b64": base64.b64encode(data).decode("ascii"),
        }
        self._get_collection().upsert(self._key(media_id), doc)
        return media_id

    def load(self, media_id: str) -> Optional[bytes]:
        """Return raw bytes, or None when the key does not exist."""
        try:
            result = self._get_collection().get(self._key(media_id))
        except Exception:
            return None
        payload = result.content_as[dict]
        raw = payload.get("data_b64", "")
        return base64.b64decode(raw) if raw else None

    def delete(self, media_id: str) -> bool:
        try:
            self._get_collection().remove(self._key(media_id))
            return True
        except Exception:
            return False

    def exists(self, media_id: str) -> bool:
        try:
            return self._get_collection().exists(self._key(media_id)).exists
        except Exception:
            return False
