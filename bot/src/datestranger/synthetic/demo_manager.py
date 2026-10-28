"""
Demo Manager & Synthetic Isolation Layer.
Controls synthetic mode (OFF, DEVELOPMENT, DEMO, LOAD_TEST),
seeds demo profiles, tracks demo sessions, and guarantees strict separation
from genuine user tables and statistics.
"""

from datetime import datetime
import os
import threading
from typing import Any, Dict, List, Optional
from datestranger.synthetic.models import SyntheticMode, SyntheticProfile
from datestranger.synthetic.generator import SyntheticProfileGenerator


class DemoManager:
    """
    Manages synthetic/demo environments, profile pools, and demo session statistics.
    Ensures zero synthetic data pollutes real member metrics.
    """

    def __init__(
        self,
        mode: SyntheticMode = SyntheticMode.DEMO,
        generator: Optional[SyntheticProfileGenerator] = None,
        db: Optional[Any] = None,
    ):
        self.mode = mode
        self.generator = generator or SyntheticProfileGenerator()
        self.db = db
        self._lock = threading.RLock()

        # In-memory demo profile pool and sessions
        self._demo_profiles: Dict[int, SyntheticProfile] = {}
        self._active_demo_conversations: Dict[str, Dict[str, Any]] = {}
        self._demo_stats = {
            "seeded_profiles_count": 0,
            "conversations_started": 0,
            "conversations_completed": 0,
            "messages_sent": 0,
            "mode": self.mode.value,
        }

        # Auto-seed initial pool of demo profiles
        self.seed_demo_profiles(count=20)

    def is_active(self) -> bool:
        return self.mode != SyntheticMode.OFF

    def set_mode(self, new_mode: SyntheticMode):
        with self._lock:
            self.mode = new_mode
            self._demo_stats["mode"] = new_mode.value

    def seed_demo_profiles(self, count: int = 20) -> List[SyntheticProfile]:
        """
        Seeds diverse synthetic profiles into the demo pool and synthetic collection.
        """
        with self._lock:
            profiles = []
            for _ in range(count):
                profile = self.generator.generate()
                self._demo_profiles[profile.synthetic_user_id] = profile
                profiles.append(profile)

                # Persist to separate MongoDB collection if DB connection exists
                if self.db is not None:
                    try:
                        synth_col = self.db["synthetic_profiles"]
                        synth_col.update_one(
                            {"synthetic_user_id": profile.synthetic_user_id},
                            {"$set": profile.to_dict()},
                            upsert=True
                        )
                    except Exception as e:
                        pass

            self._demo_stats["seeded_profiles_count"] = len(self._demo_profiles)
            return profiles

    def get_profile(self, synthetic_user_id: int) -> Optional[SyntheticProfile]:
        with self._lock:
            if synthetic_user_id in self._demo_profiles:
                return self._demo_profiles[synthetic_user_id]
            # Try DB fallback if available
            if self.db is not None:
                try:
                    synth_col = self.db["synthetic_profiles"]
                    doc = synth_col.find_one({"synthetic_user_id": synthetic_user_id})
                    if doc:
                        # Return fresh profile or reconstruct
                        pass
                except Exception:
                    pass
            return None

    def start_demo_conversation(
        self,
        real_user_id: int,
        preferred_gender: Optional[str] = None
    ) -> SyntheticProfile:
        """
        Initiates a demo conversation between a real user and a synthetic partner.
        """
        if not self.is_active():
            raise RuntimeError("Synthetic mode is OFF. Demo conversations cannot be started.")

        with self._lock:
            # Generate a new unique synthetic profile or pick from pool
            profile = self.generator.generate(preferred_gender=preferred_gender)
            self._demo_profiles[profile.synthetic_user_id] = profile

            conv_id = f"demo_{real_user_id}_{profile.synthetic_user_id}"
            self._active_demo_conversations[conv_id] = {
                "conv_id": conv_id,
                "real_user_id": real_user_id,
                "synthetic_user_id": profile.synthetic_user_id,
                "started_at": datetime.now(),
                "is_synthetic": True,
            }

            self._demo_stats["conversations_started"] += 1

            # Log to separate synthetic collections if DB is present
            if self.db is not None:
                try:
                    conv_col = self.db["synthetic_conversations"]
                    conv_col.insert_one({
                        "conv_id": conv_id,
                        "real_user_id": real_user_id,
                        "synthetic_user_id": profile.synthetic_user_id,
                        "is_synthetic": True,
                        "started_at": datetime.now(),
                    })
                except Exception:
                    pass

            return profile

    def stop_demo_conversation(self, real_user_id: int):
        with self._lock:
            matching_convs = [
                cid for cid, c in self._active_demo_conversations.items()
                if c.get("real_user_id") == real_user_id
            ]
            for cid in matching_convs:
                self._active_demo_conversations.pop(cid, None)
                self._demo_stats["conversations_completed"] += 1

                if self.db is not None:
                    try:
                        self.db["synthetic_conversations"].delete_many({"conv_id": cid})
                    except Exception:
                        pass

    def record_synthetic_message(self, conv_id: str, text: str):
        with self._lock:
            self._demo_stats["messages_sent"] += 1
            if self.db is not None:
                try:
                    self.db["synthetic_messages"].insert_one({
                        "conv_id": conv_id,
                        "is_synthetic": True,
                        "text": text,
                        "timestamp": datetime.now(),
                    })
                except Exception:
                    pass

    def reset_demo_data(self):
        """
        Resets all synthetic in-memory pools and drops synthetic collections cleanly.
        """
        with self._lock:
            self._demo_profiles.clear()
            self._active_demo_conversations.clear()
            self._demo_stats = {
                "seeded_profiles_count": 0,
                "conversations_started": 0,
                "conversations_completed": 0,
                "messages_sent": 0,
                "mode": self.mode.value,
            }

            if self.db is not None:
                try:
                    self.db["synthetic_profiles"].drop()
                    self.db["synthetic_conversations"].drop()
                    self.db["synthetic_messages"].drop()
                    self.db["synthetic_conversation_state"].drop()
                except Exception:
                    pass

            # Re-seed fresh pool
            self.seed_demo_profiles(count=20)

    def get_demo_statistics(self) -> Dict[str, Any]:
        with self._lock:
            return {
                **self._demo_stats,
                "active_demo_conversations": len(self._active_demo_conversations),
                "is_active": self.is_active(),
            }
