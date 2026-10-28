"""
Synthetic Conversation Engine Orchestrator.
Coordinates profile generation, intent classification, memory updates, state transitions,
anti-repetition checks, timing calculations, and dialogue response generation.
"""

from datetime import datetime
import random
import threading
from typing import Any, Dict, List, Optional, Tuple
from datestranger.synthetic.models import (
    ConversationMemory,
    ConversationState,
    DialogueResponse,
    SyntheticMode,
    SyntheticProfile,
    UserIntent,
)
from datestranger.synthetic.generator import SyntheticProfileGenerator
from datestranger.synthetic.classifier import IntentClassifier
from datestranger.synthetic.memory import ConversationMemoryManager
from datestranger.synthetic.state_machine import ConversationStateMachine
from datestranger.synthetic.dialogue_pool import OPENINGS_BY_PERSONALITY
from datestranger.synthetic.anti_repetition import AntiRepetitionEngine
from datestranger.synthetic.variation_engine import VariationEngine
from datestranger.synthetic.timing_engine import TimingEngine
from datestranger.synthetic.response_selector import ResponseSelector
from datestranger.synthetic.demo_manager import DemoManager


class SyntheticConversationEngine:
    """
    Complete human-like synthetic conversation system for Telegram stranger chat.
    Thread-safe, stateful, and modular.
    """

    def __init__(
        self,
        mode: SyntheticMode = SyntheticMode.DEMO,
        db: Optional[Any] = None,
        speed_multiplier: float = 1.0,
        seed: Optional[int] = None,
    ):
        self.rng = random.Random(seed) if seed is not None else random.Random()
        self.generator = SyntheticProfileGenerator(seed=seed)
        self.classifier = IntentClassifier()
        self.memory_mgr = ConversationMemoryManager()
        self.state_machine = ConversationStateMachine(rng=self.rng)
        self.anti_rep = AntiRepetitionEngine()
        self.variation = VariationEngine(rng=self.rng)
        self.timing = TimingEngine(rng=self.rng, speed_multiplier=speed_multiplier)
        self.selector = ResponseSelector(
            anti_repetition=self.anti_rep,
            variation_engine=self.variation,
            timing_engine=self.timing,
            rng=self.rng,
        )
        self.demo_mgr = DemoManager(mode=mode, generator=self.generator, db=db)
        self._conv_locks: Dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()

    def _get_conv_lock(self, conv_id: str) -> threading.Lock:
        with self._global_lock:
            if conv_id not in self._conv_locks:
                self._conv_locks[conv_id] = threading.Lock()
            return self._conv_locks[conv_id]

    def create_conversation(
        self,
        real_user_id: int,
        preferred_gender: Optional[str] = None
    ) -> Tuple[str, SyntheticProfile]:
        """
        Creates a new unique synthetic companion profile and initiates a session.
        Returns (conv_id, profile).
        """
        profile = self.demo_mgr.start_demo_conversation(
            real_user_id=real_user_id,
            preferred_gender=preferred_gender,
        )
        # FREEZE PROFILE (do not regenerate)
        profile.age_frozen = profile.age
        profile.gender_frozen = profile.gender
        profile.name_frozen = profile.display_name

        conv_id = f"synth_{real_user_id}_{profile.synthetic_user_id}"
        self.memory_mgr.get_or_create(conv_id, profile)
        return conv_id, profile

    def generate_opening(self, conv_id: str) -> DialogueResponse:
        """
        Selects and styles an opening greeting message matching the synthetic profile.
        """
        with self._get_conv_lock(conv_id):
            memory = self.memory_mgr.get(conv_id)
            if not memory:
                raise ValueError(f"Conversation {conv_id} not found in memory.")

            profile = memory.synthetic_profile
            openings = OPENINGS_BY_PERSONALITY.get(profile.personality, OPENINGS_BY_PERSONALITY[profile.personality.CASUAL])

            # Filter openings by anti-repetition penalty
            available = [
                op for op in openings
                if self.anti_rep.score_repetition_penalty(op["text"], memory.recent_synthetic_replies) > 0.0
            ]
            if not available:
                available = openings

            chosen = self.rng.choice(available)
            raw_text = chosen["text"]
            styled_text = self.variation.apply_style(raw_text, profile)
            delay = self.timing.calculate_reply_delay(profile, len(styled_text), is_opening=True)

            # Record in anti-repetition and memory
            self.anti_rep.record_used_opening(raw_text)
            self.memory_mgr.record_turn(
                conv_id=conv_id,
                user_text="[SESSION_START]",
                synthetic_text=styled_text,
                intent_names=["SESSION_START"],
            )

            self.demo_mgr.record_synthetic_message(conv_id, styled_text)

            return DialogueResponse(
                text=styled_text,
                delay_seconds=delay,
                state_after=ConversationState.INTRO,
                should_end_conversation=False,
                debug_notes={
                    "opening_template": raw_text,
                    "personality": profile.personality.value,
                    "delay": delay,
                },
            )

    def handle_user_message(self, conv_id: str, user_text: str, message_id: Optional[int] = None) -> DialogueResponse:
        """
        Processes incoming user text, updates memory, transitions state, and returns response.
        Thread-safe per conversation ID to prevent reply collisions or race conditions.
        """
        with self._get_conv_lock(conv_id):
            memory = self.memory_mgr.get(conv_id)
            if not memory:
                print(f"[ENGINE] Conv {conv_id} not in memory, aborting")
                raise ValueError(f"Conversation {conv_id} not found.")

            if not memory.is_active or memory.has_ended or getattr(memory, "cancellation_requested", False):
                return DialogueResponse(
                    text="",
                    delay_seconds=0.0,
                    state_after=ConversationState.ENDED,
                    should_end_conversation=True,
                    debug_notes={"aborted": "session_not_active"},
                )

            # Deduplication check
            if message_id is not None:
                if message_id in memory.processed_message_ids:
                    return DialogueResponse(
                        text="",
                        delay_seconds=0.0,
                        state_after=memory.current_state,
                        should_end_conversation=False,
                        debug_notes={"aborted": "duplicate_event_id", "message_id": message_id},
                    )
                memory.processed_message_ids.add(message_id)
                memory.last_processed_message_id = message_id

            # Mark greeting as sent / user spoke first
            memory.greeting_sent = True

            profile = memory.synthetic_profile

            # 1. Classify user message with prior context
            prior_messages = list(memory.recent_user_messages[-5:]) if memory.recent_user_messages else []
            open_questions = [memory.last_question_asked_by_bot] if memory.last_question_asked_by_bot else []
            classified = self.classifier.classify(
                text=user_text,
                prior_messages=prior_messages,
                open_questions=open_questions,
            )

            # 2. Update memory with any extracted entities
            if classified.extracted_entities:
                for k, v in classified.extracted_entities.items():
                    memory.remember_user_fact(k, v)

            # 3. Determine state transition and whether to exit
            next_state, should_end = self.state_machine.determine_next_state(
                memory=memory,
                profile=profile,
                primary_intent=classified.primary_intent(),
                all_intents=classified.intents,
            )

            # 4. Select and format response
            response = self.selector.select_response(
                classified=classified,
                memory=memory,
                profile=profile,
                next_state=next_state,
                should_end=should_end,
            )

            # 5. Record turn into memory
            self.memory_mgr.update_state(conv_id, response.state_after)
            self.memory_mgr.record_turn(
                conv_id=conv_id,
                user_text=user_text,
                synthetic_text=response.text,
                intent_names=[i.value for i in classified.intents],
                entities=classified.extracted_entities,
                asked_question=response.debug_notes.get("topic_asked"),
            )

            # 6. Record to demo manager
            self.demo_mgr.record_synthetic_message(conv_id, response.text)
            if response.is_double_message and response.second_message_text:
                self.demo_mgr.record_synthetic_message(conv_id, response.second_message_text)

            if response.should_end_conversation:
                self.memory_mgr.end_conversation(conv_id, reason="natural_completion")

            # 7. Attach debug notes
            response.debug_notes.update({
                "classified_intents": [i.value for i in classified.intents],
                "extracted_entities": classified.extracted_entities,
                "current_state": memory.current_state.value,
                "messages_exchanged": memory.messages_exchanged,
                "personality": profile.personality.value,
                "is_synthetic": True,
            })

            return response

    def get_conversation_debug_info(self, conv_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves detailed state machine, personality, classified intent, and memory info for admin.
        """
        memory = self.memory_mgr.get(conv_id)
        if not memory:
            return None

        profile = memory.synthetic_profile
        return {
            "conv_id": conv_id,
            "is_synthetic": True,
            "synthetic_user_id": profile.synthetic_user_id,
            "display_name": profile.display_name,
            "gender": profile.gender,
            "age": profile.age,
            "location": profile.location,
            "personality": profile.personality.value,
            "texting_style": profile.texting_style.value,
            "current_state": memory.current_state.value,
            "messages_exchanged": memory.messages_exchanged,
            "user_gender": memory.user_gender,
            "user_location": memory.user_location,
            "user_age": memory.user_age,
            "user_interest": memory.user_interest,
            "asked_questions": memory.asked_questions,
            "shared_facts": memory.shared_facts,
            "has_ended": memory.has_ended,
            "ended_reason": memory.ended_reason,
            "last_activity": memory.last_activity.isoformat() if memory.last_activity else None,
        }

    def end_conversation(self, conv_id: str, reason: str = "user_disconnected"):
        self.memory_mgr.end_conversation(conv_id, reason=reason)
        with self._global_lock:
            self._conv_locks.pop(conv_id, None)

    def simulate_conversation(
        self,
        user_inputs: List[str],
        preferred_gender: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Helper method to run an automated synthetic conversation simulation for testing.
        """
        test_uid = self.rng.randint(100000, 999999)
        conv_id, profile = self.create_conversation(test_uid, preferred_gender=preferred_gender)
        opening_resp = self.generate_opening(conv_id)

        transcript = [{"speaker": "synthetic", "text": opening_resp.text, "delay": opening_resp.delay_seconds}]

        for u_msg in user_inputs:
            mem = self.memory_mgr.get(conv_id)
            if mem and mem.has_ended:
                break
            resp = self.handle_user_message(conv_id, u_msg)
            transcript.append({"speaker": "user", "text": u_msg})
            transcript.append({"speaker": "synthetic", "text": resp.text, "delay": resp.delay_seconds})
            if resp.is_double_message and resp.second_message_text:
                transcript.append({
                    "speaker": "synthetic",
                    "text": resp.second_message_text,
                    "delay": resp.second_message_delay,
                    "is_double": True,
                })
            if resp.should_end_conversation:
                break

        debug_info = self.get_conversation_debug_info(conv_id)
        return {
            "conv_id": conv_id,
            "profile": profile.to_dict(),
            "transcript": transcript,
            "debug_info": debug_info,
        }
