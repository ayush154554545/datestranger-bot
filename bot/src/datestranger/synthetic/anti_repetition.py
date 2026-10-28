"""
Anti-Repetition Engine.
Enforces strict bans on canned AI chatbot phrases and penalizes recent phrases,
openings, and question loops to ensure high conversational entropy.
"""

from collections import deque
import re
import threading
from typing import List, Set


# Strictly prohibited AI-sounding phrases
PROHIBITED_AI_PHRASES = [
    r"that sounds great",
    r"that sounds wonderful",
    r"that must be exciting",
    r"i'?d love to hear more",
    r"what else are you into",
    r"that sounds interesting",
    r"tell me more about that",
    r"how does that make you feel",
    r"as an ai",
    r"i am here to assist",
    r"glad we matched \ud83d\ude0a",
    r"how do you do",
    r"thanks for sharing",
]


class AntiRepetitionEngine:
    """
    Maintains global and conversation-level history of used utterances,
    strictly blocks canned phrases, and penalizes repetitive branches.
    """

    def __init__(self, global_history_size: int = 50, cooldown_count: int = 5):
        self._lock = threading.Lock()
        self.global_recent_openings: deque = deque(maxlen=global_history_size)
        self.global_recent_replies: deque = deque(maxlen=global_history_size)
        self.cooldown_count = cooldown_count

    def is_ai_prohibited(self, text: str) -> bool:
        """Checks if text contains banned corporate or robotic AI phrases."""
        low = text.lower().strip()
        for pattern in PROHIBITED_AI_PHRASES:
            if re.search(pattern, low):
                return True
        return False

    def score_repetition_penalty(
        self,
        candidate_text: str,
        conversation_history: List[str],
        recent_questions: List[str] = None
    ) -> float:
        """
        Returns a score multiplier between 0.0 (unusable) and 1.0 (fresh).
        """
        if self.is_ai_prohibited(candidate_text):
            return 0.0

        low_cand = candidate_text.lower().strip()
        # Normalize for strict comparison (remove emojis, extra spaces, punctuation)
        clean_cand = re.sub(r"[^\w\s]", "", low_cand).strip()

        # Check against recent conversation history
        for past_msg in conversation_history:
            low_past = past_msg.lower().strip()
            clean_past = re.sub(r"[^\w\s]", "", low_past).strip()

            # Exact match or normalized match penalty
            if low_cand == low_past or (clean_cand and clean_cand == clean_past):
                return 0.0

            # Substring / high overlap check
            if len(clean_cand) > 10 and clean_cand in clean_past:
                return 0.0
            if len(clean_past) > 10 and clean_past in clean_cand:
                return 0.0

        # Check global recent openings / replies
        with self._lock:
            if candidate_text in self.global_recent_openings:
                return 0.05
            if candidate_text in self.global_recent_replies:
                return 0.1

        return 1.0

    def record_used_opening(self, opening_text: str):
        with self._lock:
            self.global_recent_openings.append(opening_text)

    def record_used_reply(self, reply_text: str):
        with self._lock:
            self.global_recent_replies.append(reply_text)
