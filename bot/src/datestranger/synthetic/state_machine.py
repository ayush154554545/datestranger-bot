"""
Conversation State Machine.
Controls non-linear progression across conversation states and natural termination.
"""

import random
from typing import Optional, Tuple
from datestranger.synthetic.models import (
    ConversationState,
    ConversationMemory,
    SyntheticProfile,
    UserIntent,
    PersonalityType,
)


class ConversationStateMachine:
    """
    Evaluates state transitions based on turn count, user intents, synthetic personality,
    and profile exit probabilities.
    """

    def __init__(self, rng: Optional[random.Random] = None):
        self.rng = rng or random.Random()

    def determine_next_state(
        self,
        memory: ConversationMemory,
        profile: SyntheticProfile,
        primary_intent: UserIntent,
        all_intents: list,
    ) -> Tuple[ConversationState, bool]:
        """
        Returns (next_state, should_end_now).
        """
        curr = memory.current_state
        turns = memory.messages_exchanged

        # If already ended
        if curr == ConversationState.ENDED or memory.has_ended:
            return ConversationState.ENDED, True

        # Immediate exit triggers from user
        if primary_intent in [UserIntent.BYE] or UserIntent.BYE in all_intents:
            return ConversationState.ENDING, True

        # Check disinterest progression
        if primary_intent == UserIntent.DISINTEREST or (
            UserIntent.SHORT_REPLY in all_intents and turns >= 3 and profile.personality in [PersonalityType.DRY_TEXTER, PersonalityType.BORED, PersonalityType.QUIET]
        ):
            if curr == ConversationState.DISINTERESTED or turns >= profile.min_exchanges_before_exit:
                return ConversationState.ENDING, True
            return ConversationState.DISINTERESTED, False

        # Natural exit check:
        # After minimum turns, roll profile exit_probability
        if turns >= profile.min_exchanges_before_exit:
            # The more turns pass beyond minimum, the exit chance increases slightly
            turn_multiplier = 1.0 + (turns - profile.min_exchanges_before_exit) * 0.08
            effective_exit_chance = min(0.65, profile.exit_probability * turn_multiplier)
            if self.rng.random() < effective_exit_chance:
                return ConversationState.ENDING, True

        # State transitions based on current state and intents
        if curr == ConversationState.INTRO:
            if primary_intent in [UserIntent.GENDER_MALE, UserIntent.GENDER_FEMALE, UserIntent.LOCATION, UserIntent.AGE]:
                return ConversationState.GETTING_TO_KNOW, False
            elif primary_intent in [UserIntent.BORED, UserIntent.LOOKING_FOR_CHAT]:
                return ConversationState.CASUAL_CHAT, False
            elif primary_intent == UserIntent.FLIRTING:
                return ConversationState.PLAYFUL, False
            else:
                return ConversationState.GETTING_TO_KNOW, False

        elif curr == ConversationState.GETTING_TO_KNOW:
            if primary_intent == UserIntent.INTEREST:
                return ConversationState.INTEREST_DISCOVERY, False
            elif primary_intent == UserIntent.FLIRTING:
                return ConversationState.PLAYFUL, False
            elif primary_intent == UserIntent.CONFUSION:
                return ConversationState.AWKWARD, False
            elif turns >= 3:
                return ConversationState.CASUAL_CHAT, False
            return ConversationState.GETTING_TO_KNOW, False

        elif curr == ConversationState.CASUAL_CHAT:
            if primary_intent == UserIntent.INTEREST:
                return ConversationState.INTEREST_DISCOVERY, False
            elif primary_intent == UserIntent.FLIRTING:
                return ConversationState.PLAYFUL, False
            elif turns >= 5:
                # Branch between PERSONAL_TOPIC and INTEREST_DISCOVERY
                branch = self.rng.choice([ConversationState.PERSONAL_TOPIC, ConversationState.INTEREST_DISCOVERY])
                return branch, False
            return ConversationState.CASUAL_CHAT, False

        elif curr == ConversationState.INTEREST_DISCOVERY:
            if primary_intent == UserIntent.FLIRTING:
                return ConversationState.PLAYFUL, False
            elif turns >= 6:
                return ConversationState.CASUAL_CHAT, False
            return ConversationState.INTEREST_DISCOVERY, False

        elif curr == ConversationState.PLAYFUL:
            if primary_intent in [UserIntent.DISINTEREST, UserIntent.NEGATIVE]:
                return ConversationState.AWKWARD, False
            return ConversationState.PLAYFUL, False

        elif curr == ConversationState.AWKWARD:
            if primary_intent in [UserIntent.GREETING, UserIntent.POSITIVE]:
                return ConversationState.CASUAL_CHAT, False
            # Awkward conversations often end early
            if self.rng.random() < 0.35:
                return ConversationState.ENDING, True
            return ConversationState.CASUAL_CHAT, False

        elif curr == ConversationState.DISINTERESTED:
            if self.rng.random() < 0.50:
                return ConversationState.ENDING, True
            return ConversationState.ENDING, True

        elif curr == ConversationState.ENDING:
            return ConversationState.ENDED, True

        return ConversationState.CASUAL_CHAT, False
