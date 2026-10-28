"""
Response Selector.
Selects contextually appropriate, non-repetitive dialogue branches using weighted
randomness, topic alternation, memory constraints, and anti-repetition scoring.
Strictly adheres to Priority 1 through Priority 7 message handling.
"""

import random
from typing import Dict, List, Optional, Tuple
from datestranger.synthetic.models import (
    ConversationMemory,
    ConversationState,
    DialogueResponse,
    PersonalityType,
    SyntheticProfile,
    UserIntent,
)
from datestranger.synthetic.classifier import ClassifiedMessage
from datestranger.synthetic.dialogue_pool import (
    GENDER_REPLIES,
    LOCATION_REPLIES,
    SYNTHETIC_LOCATION_DISCLOSURES,
    BOREDOM_REPLIES,
    SHORT_REPLY_REACTIONS,
    INTEREST_REPLIES,
    NATURAL_ENDINGS,
    DOUBLE_MESSAGE_PAIRS,
    HOW_ARE_YOU_REPLIES,
    NAME_DISCLOSURES,
    AGE_DISCLOSURES,
    GENDER_DISCLOSURES_FEMALE,
    GENDER_DISCLOSURES_MALE,
    REASON_DISCLOSURES,
    DOING_DISCLOSURES,
    CHALLENGE_MAD_REPLIES,
    CHALLENGE_BOT_REPLIES,
    CONFUSION_REPLIES,
    ANSWER_NO_REACTIONS,
    ANSWER_YES_REACTIONS,
    ANSWER_NOTHING_REACTIONS,
    UNKNOWN_ANSWER_REACTIONS,
    GREETING_REPLIES,
    LOCATION_ANSWER_ACKNOWLEDGMENTS,
    ACTIVITY_ANSWER_ACKNOWLEDGMENTS,
    MUSIC_ANSWER_ACKNOWLEDGMENTS,
)
from datestranger.synthetic.anti_repetition import AntiRepetitionEngine
from datestranger.synthetic.variation_engine import VariationEngine
from datestranger.synthetic.timing_engine import TimingEngine


class ResponseSelector:
    """
    Evaluates candidate responses against user input, intent, state, memory, and anti-repetition.
    Follows strict priority ordering:
    Priority 1: Stop/Leave/Disconnect commands
    Priority 2: Session validation and duplicate detection (handled at dispatcher/entry)
    Priority 3: Direct inquiries and challenges
    Priority 4: Answers to the bot's previous questions
    Priority 5: Continuation of current topic
    Priority 6: Greetings, small talk, casual banter
    Priority 7: Neutral clarification fallback
    """

    def __init__(
        self,
        anti_repetition: AntiRepetitionEngine,
        variation_engine: VariationEngine,
        timing_engine: TimingEngine,
        rng: Optional[random.Random] = None,
    ):
        self.anti_rep = anti_repetition
        self.variation = variation_engine
        self.timing = timing_engine
        self.rng = rng or random.Random()

    def select_response(
        self,
        classified: ClassifiedMessage,
        memory: ConversationMemory,
        profile: SyntheticProfile,
        next_state: ConversationState,
        should_end: bool,
    ) -> DialogueResponse:
        """
        Picks and styles the best response branch based on state, intent, and memory.
        """
        primary = classified.primary_intent()

        # Enforce persona consistency against frozen baseline
        if hasattr(profile, "age_frozen") and profile.age_frozen is not None:
            if profile.age != profile.age_frozen:
                print(f"[WARN] Persona age mismatch: frozen={profile.age_frozen}, current={profile.age}")
                profile.age = profile.age_frozen
        if hasattr(profile, "gender_frozen") and profile.gender_frozen is not None:
            if profile.gender != profile.gender_frozen:
                print(f"[WARN] Persona gender mismatch: frozen={profile.gender_frozen}, current={profile.gender}")
                profile.gender = profile.gender_frozen

        # Priority 1: Immediate Stop / Exit Commands
        if primary == UserIntent.COMMAND_STOP:
            if memory:
                memory.has_ended = True
                memory.is_active = False
                memory.ended_reason = "user_stop_command"
            return DialogueResponse(
                text="",
                delay_seconds=0.0,
                state_after=ConversationState.ENDED,
                should_end_conversation=True,
                debug_notes={"branch": "stop_command", "intent": "COMMAND_STOP"},
            )

        if should_end or next_state in [ConversationState.ENDING, ConversationState.ENDED] or primary in [UserIntent.BYE, UserIntent.DISINTEREST]:
            return self._select_ending_response(memory, profile)

        # Check for rare double message (only when user didn't ask a question and not a direct inquiry)
        is_direct_inquiry = primary in [
            UserIntent.ASK_HOW_ARE_YOU,
            UserIntent.ASK_NAME,
            UserIntent.ASK_LOCATION,
            UserIntent.ASK_AGE,
            UserIntent.ASK_GENDER,
            UserIntent.ASK_REASON,
            UserIntent.ASK_DOING,
            UserIntent.CHALLENGE_MAD,
            UserIntent.CHALLENGE_BOT,
            UserIntent.CONFUSION,
        ]

        if (
            not classified.is_question
            and not is_direct_inquiry
            and self.rng.random() < profile.double_message_probability
            and memory.messages_exchanged >= 2
        ):
            pair = self.rng.choice(DOUBLE_MESSAGE_PAIRS)
            first_text = self.variation.apply_style(pair["first"], profile)
            second_text = self.variation.apply_style(pair["second"], profile)
            first_delay = self.timing.calculate_reply_delay(profile, len(first_text))
            second_delay = pair.get("second_delay", 2.0)

            self.anti_rep.record_used_reply(first_text)
            self.anti_rep.record_used_reply(second_text)

            return DialogueResponse(
                text=first_text,
                delay_seconds=first_delay,
                is_double_message=True,
                second_message_text=second_text,
                second_message_delay=second_delay,
                state_after=next_state,
                should_end_conversation=False,
                debug_notes={"branch": "double_message", "intent": "DOUBLE_TRIGGER"},
            )

        candidates: List[Dict] = []
        topic_asked: Optional[str] = None

        # Priority 3: Direct User Inquiries & Challenges
        if primary == UserIntent.ASK_HOW_ARE_YOU:
            candidates = HOW_ARE_YOU_REPLIES
            topic_asked = "how_are_you"

        elif primary == UserIntent.ASK_NAME:
            candidates = NAME_DISCLOSURES
            topic_asked = "name"

        elif primary == UserIntent.ASK_LOCATION:
            candidates = SYNTHETIC_LOCATION_DISCLOSURES
            topic_asked = "location"

        elif primary == UserIntent.ASK_AGE:
            candidates = AGE_DISCLOSURES
            topic_asked = "age"

        elif primary == UserIntent.ASK_GENDER:
            candidates = GENDER_DISCLOSURES_FEMALE if profile.gender == "female" else GENDER_DISCLOSURES_MALE
            topic_asked = "gender"

        elif primary == UserIntent.ASK_REASON:
            candidates = REASON_DISCLOSURES
            topic_asked = "reason"

        elif primary == UserIntent.ASK_DOING:
            candidates = DOING_DISCLOSURES
            topic_asked = "doing"

        elif primary == UserIntent.CHALLENGE_MAD:
            candidates = CHALLENGE_MAD_REPLIES

        elif primary == UserIntent.CHALLENGE_BOT:
            candidates = CHALLENGE_BOT_REPLIES

        elif primary == UserIntent.CONFUSION:
            candidates = CONFUSION_REPLIES

        # Priority 4: User Answering Previous Questions Asked by Bot
        elif memory and memory.last_question_asked_by_bot:
            last_q = memory.last_question_asked_by_bot
            if last_q == "location" and (primary == UserIntent.LOCATION or "user_location" in classified.extracted_entities or not classified.is_question):
                candidates = LOCATION_ANSWER_ACKNOWLEDGMENTS
                memory.last_question_asked_by_bot = None
            elif last_q in ["activity", "plans", "hobbies"] and not classified.is_question:
                candidates = ACTIVITY_ANSWER_ACKNOWLEDGMENTS
                memory.last_question_asked_by_bot = None
            elif last_q == "music" and not classified.is_question:
                candidates = MUSIC_ANSWER_ACKNOWLEDGMENTS
                memory.last_question_asked_by_bot = None

        # Priority 5: Continuation of Current Topic & User Shared Facts
        if not candidates:
            if primary in [UserIntent.GENDER_MALE, UserIntent.GENDER_FEMALE]:
                user_g = "male" if primary == UserIntent.GENDER_MALE else "female"
                synth_g = profile.gender
                key = f"user_{user_g}_synthetic_{synth_g}"
                candidates = GENDER_REPLIES.get(key, [])

            elif primary == UserIntent.LOCATION or "user_location" in classified.extracted_entities:
                candidates = LOCATION_REPLIES

            elif primary == UserIntent.INTEREST or "user_interest" in classified.extracted_entities:
                candidates = INTEREST_REPLIES

            elif primary == UserIntent.BORED:
                candidates = BOREDOM_REPLIES

        # Priority 6: Greetings, Small Talk, and Short Answers
        if not candidates:
            if primary == UserIntent.GREETING:
                candidates = GREETING_REPLIES

            elif primary == UserIntent.USER_ANSWER_NO:
                candidates = ANSWER_NO_REACTIONS

            elif primary == UserIntent.USER_ANSWER_YES:
                candidates = ANSWER_YES_REACTIONS

            elif primary == UserIntent.USER_ANSWER_NOTHING:
                candidates = ANSWER_NOTHING_REACTIONS

            elif primary in [UserIntent.AGE_UNKNOWN, UserIntent.UNKNOWN_ANSWER]:
                candidates = UNKNOWN_ANSWER_REACTIONS
                if memory:
                    memory.last_question_asked_by_bot = None

            elif primary in [UserIntent.SHORT_REPLY, UserIntent.POSITIVE, UserIntent.UNKNOWN]:
                candidates = SHORT_REPLY_REACTIONS.get(profile.personality, SHORT_REPLY_REACTIONS[PersonalityType.CASUAL])

        # Priority 7: Neutral Fallback
        if not candidates:
            candidates = SHORT_REPLY_REACTIONS.get(profile.personality, SHORT_REPLY_REACTIONS[PersonalityType.CASUAL])

        # Memory & Anti-repetition filter:
        # 1. Do NOT pick candidates with 0.0 repetition penalty
        # 2. Do NOT ask a question that was already asked or answered!
        filtered_candidates = []
        for cand in candidates:
            text = cand.get("text", "")
            if memory and memory.recent_synthetic_replies:
                penalty = self.anti_rep.score_repetition_penalty(text, memory.recent_synthetic_replies)
                if penalty <= 0.0:
                    try:
                        print(f"[ANTI-REP] Filtered: {text[:50]} (penalty={penalty})")
                    except UnicodeEncodeError:
                        safe_snippet = text[:50].encode("ascii", "replace").decode("ascii")
                        print(f"[ANTI-REP] Filtered: {safe_snippet} (penalty={penalty})")
                    continue

            asks = cand.get("asks")
            if asks and memory:
                if asks == "location" and (memory.user_location or "location" in memory.asked_questions):
                    continue
                if asks == "gender" and (memory.user_gender or "gender" in memory.asked_questions):
                    continue
                if asks == "interest" and (memory.user_interest or "interest" in memory.asked_questions):
                    continue
                if asks in memory.asked_questions:
                    continue
            filtered_candidates.append(cand)

        if not filtered_candidates:
            # If all candidates were filtered, pick one whose raw text hasn't appeared yet
            filtered_candidates = [
                c for c in candidates
                if not (memory and any(c.get("text", "").strip().lower() in r.strip().lower() for r in memory.recent_synthetic_replies))
            ] or candidates

        # Weighted selection with anti-repetition penalties
        chosen_dict = self._weighted_choice_with_penalties(filtered_candidates, memory)
        raw_reply = chosen_dict.get("text", "fair enough")
        if chosen_dict.get("asks"):
            topic_asked = chosen_dict["asks"]
            if memory:
                memory.last_question_asked_by_bot = topic_asked

        # Apply realistic variation (typos, casing, emojis, profile placeholders)
        final_text = self.variation.apply_style(raw_reply, profile)

        # Calculate timing
        delay = self.timing.calculate_reply_delay(profile, len(final_text))

        # Record into anti-repetition engine
        self.anti_rep.record_used_reply(final_text)

        return DialogueResponse(
            text=final_text,
            delay_seconds=delay,
            is_double_message=False,
            state_after=next_state,
            should_end_conversation=False,
            debug_notes={
                "branch": chosen_dict.get("text"),
                "intent": primary.value,
                "topic_asked": topic_asked,
                "score_weight": chosen_dict.get("weight", 1.0),
            },
        )

    def _select_ending_response(self, memory: ConversationMemory, profile: SyntheticProfile) -> DialogueResponse:
        filtered = [
            e for e in NATURAL_ENDINGS
            if self.anti_rep.score_repetition_penalty(e["text"], memory.recent_synthetic_replies) > 0.0
        ]
        if not filtered:
            filtered = NATURAL_ENDINGS
        ending = self.rng.choice(filtered)
        text = self.variation.apply_style(ending["text"], profile)
        delay = self.timing.calculate_reply_delay(profile, len(text))
        self.anti_rep.record_used_reply(text)

        return DialogueResponse(
            text=text,
            delay_seconds=delay,
            is_double_message=False,
            state_after=ConversationState.ENDED,
            should_end_conversation=True,
            debug_notes={"branch": "natural_ending", "ending_phrase": ending["text"]},
        )

    def _weighted_choice_with_penalties(self, candidates: List[Dict], memory: ConversationMemory) -> Dict:
        scored = []
        weights = []
        for cand in candidates:
            text = cand.get("text", "")
            base_w = cand.get("weight", 0.20)
            rep_multiplier = self.anti_rep.score_repetition_penalty(text, memory.recent_synthetic_replies)
            if rep_multiplier <= 0.0:
                continue
            final_w = base_w * rep_multiplier
            scored.append(cand)
            weights.append(max(0.001, final_w))

        if not scored:
            return self.rng.choice(candidates)

        return self.rng.choices(scored, weights=weights, k=1)[0]
