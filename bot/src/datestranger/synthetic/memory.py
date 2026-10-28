"""
Conversation Memory Manager.
Maintains stateful memory per synthetic conversation session to ensure
facts (gender, location, interests, age) are remembered and never re-asked.
"""

from datetime import datetime, timedelta
import threading
from typing import Dict, Optional
from datestranger.synthetic.models import ConversationMemory, SyntheticProfile, ConversationState


class ConversationMemoryManager:
    """
    Thread-safe in-memory store for active synthetic conversations with TTL cleanup.
    """

    def __init__(self, ttl_minutes: int = 120):
        self._memories: Dict[str, ConversationMemory] = {}
        self._lock = threading.RLock()
        self.ttl = timedelta(minutes=ttl_minutes)

    def get_or_create(self, conv_id: str, profile: SyntheticProfile) -> ConversationMemory:
        with self._lock:
            self._cleanup_expired()
            if conv_id not in self._memories:
                self._memories[conv_id] = ConversationMemory(
                    conv_id=conv_id,
                    synthetic_profile=profile,
                    synthetic_personality=profile.personality.value,
                    current_state=ConversationState.INTRO,
                    messages_exchanged=0,
                )
            memory = self._memories[conv_id]
            memory.last_activity = datetime.now()
            return memory

    def get(self, conv_id: str) -> Optional[ConversationMemory]:
        with self._lock:
            mem = self._memories.get(conv_id)
            if mem:
                mem.last_activity = datetime.now()
            return mem

    def update_state(self, conv_id: str, new_state: ConversationState):
        with self._lock:
            mem = self._memories.get(conv_id)
            if mem:
                mem.current_state = new_state
                mem.last_activity = datetime.now()

    def record_turn(
        self,
        conv_id: str,
        user_text: str,
        synthetic_text: str,
        intent_names: list,
        entities: dict = None,
        asked_question: Optional[str] = None,
    ):
        with self._lock:
            mem = self._memories.get(conv_id)
            if not mem:
                return

            mem.messages_exchanged += 1
            mem.recent_user_messages.append(user_text)
            if len(mem.recent_user_messages) > 30:
                mem.recent_user_messages.pop(0)

            mem.recent_synthetic_replies.append(synthetic_text)
            if len(mem.recent_synthetic_replies) > 30:
                mem.recent_synthetic_replies.pop(0)

            mem.recent_intents.extend(intent_names)
            if len(mem.recent_intents) > 50:
                mem.recent_intents = mem.recent_intents[-50:]

            if asked_question:
                mem.asked_questions.append(asked_question)
                mem.last_question_asked_by_bot = asked_question

            if entities:
                for k, v in entities.items():
                    mem.remember_user_fact(k, v)

            mem.last_activity = datetime.now()

    def has_asked_about(self, conv_id: str, topic: str) -> bool:
        with self._lock:
            mem = self._memories.get(conv_id)
            if not mem:
                return False
            # If user already shared it or bot already asked it
            if topic == "location" and (mem.user_location or "location" in mem.asked_questions):
                return True
            if topic == "gender" and (mem.user_gender or "gender" in mem.asked_questions):
                return True
            if topic == "age" and (mem.user_age or "age" in mem.asked_questions):
                return True
            if topic == "interest" and (mem.user_interest or "interest" in mem.asked_questions):
                return True
            return topic in mem.asked_questions

    def end_conversation(self, conv_id: str, reason: str = "natural_exit"):
        with self._lock:
            mem = self._memories.get(conv_id)
            if mem:
                mem.has_ended = True
                mem.is_active = False
                mem.cancellation_requested = True
                mem.ended_reason = reason
                mem.current_state = ConversationState.ENDED

    def remove(self, conv_id: str):
        with self._lock:
            removed = self._memories.pop(conv_id, None)
            if removed:
                print(f"[MEMORY] Removed conversation {conv_id}")

    def _cleanup_expired(self):
        now = datetime.now()
        expired = [cid for cid, m in self._memories.items() if now - m.last_activity > self.ttl]
        for cid in expired:
            self._memories.pop(cid, None)

    def active_conversations_count(self) -> int:
        with self._lock:
            return len([m for m in self._memories.values() if not m.has_ended])
