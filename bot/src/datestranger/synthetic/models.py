"""
Data models and enumerations for the Human-like Synthetic Conversation Engine.
Every synthetic entity includes `is_synthetic = True` for strict data separation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class SyntheticMode(str, Enum):
    OFF = "OFF"
    DEVELOPMENT = "DEVELOPMENT"
    DEMO = "DEMO"
    LOAD_TEST = "LOAD_TEST"


class PersonalityType(str, Enum):
    CASUAL = "CASUAL"
    FRIENDLY = "FRIENDLY"
    SHY = "SHY"
    DIRECT = "DIRECT"
    BORED = "BORED"
    CURIOUS = "CURIOUS"
    DRY_TEXTER = "DRY_TEXTER"
    ENERGETIC = "ENERGETIC"
    SLIGHTLY_AWKWARD = "SLIGHTLY_AWKWARD"
    QUIET = "QUIET"


class TextingStyle(str, Enum):
    LOWERCASE = "LOWERCASE"
    CASUAL_SLANG = "CASUAL_SLANG"
    PUNCTUATED = "PUNCTUATED"
    MINIMAL = "MINIMAL"
    EXPRESSIVE = "EXPRESSIVE"


class VerbosityType(str, Enum):
    VERY_SHORT = "VERY_SHORT"
    SHORT = "SHORT"
    MEDIUM = "MEDIUM"
    LONGER = "LONGER"


class DelayProfile(str, Enum):
    FAST = "FAST"              # 2-8s
    NORMAL = "NORMAL"          # 8-25s
    SLOW = "SLOW"              # 20-90s
    INCONSISTENT = "INCONSISTENT"  # fluctuates between fast and slow


class ConversationState(str, Enum):
    INTRO = "INTRO"
    GETTING_TO_KNOW = "GETTING_TO_KNOW"
    CASUAL_CHAT = "CASUAL_CHAT"
    INTEREST_DISCOVERY = "INTEREST_DISCOVERY"
    PERSONAL_TOPIC = "PERSONAL_TOPIC"
    PLAYFUL = "PLAYFUL"
    AWKWARD = "AWKWARD"
    DISINTERESTED = "DISINTERESTED"
    ENDING = "ENDING"
    ENDED = "ENDED"


class UserIntent(str, Enum):
    GREETING = "GREETING"
    INTRODUCTION = "INTRODUCTION"
    GENDER_MALE = "GENDER_MALE"
    GENDER_FEMALE = "GENDER_FEMALE"
    LOCATION = "LOCATION"
    AGE = "AGE"
    INTEREST = "INTEREST"
    BORED = "BORED"
    LOOKING_FOR_FRIENDS = "LOOKING_FOR_FRIENDS"
    LOOKING_FOR_CHAT = "LOOKING_FOR_CHAT"
    FLIRTING = "FLIRTING"
    SHORT_REPLY = "SHORT_REPLY"
    LONG_REPLY = "LONG_REPLY"
    QUESTION = "QUESTION"
    CONFUSION = "CONFUSION"
    DISINTEREST = "DISINTEREST"
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    BYE = "BYE"
    # Specific direct user inquiries about synthetic partner
    ASK_HOW_ARE_YOU = "ASK_HOW_ARE_YOU"
    ASK_NAME = "ASK_NAME"
    ASK_LOCATION = "ASK_LOCATION"
    ASK_AGE = "ASK_AGE"
    ASK_GENDER = "ASK_GENDER"
    ASK_REASON = "ASK_REASON"
    ASK_DOING = "ASK_DOING"
    CHALLENGE_MAD = "CHALLENGE_MAD"
    CHALLENGE_BOT = "CHALLENGE_BOT"
    USER_ANSWER_NO = "USER_ANSWER_NO"
    USER_ANSWER_YES = "USER_ANSWER_YES"
    USER_ANSWER_NOTHING = "USER_ANSWER_NOTHING"
    AGE_UNKNOWN = "age_unknown"
    UNKNOWN_ANSWER = "unknown_answer"
    COMMAND_STOP = "COMMAND_STOP"
    UNKNOWN = "UNKNOWN"


@dataclass
class SyntheticProfile:
    synthetic_user_id: int
    gender: str                        # "male" | "female"
    age_range: str                     # e.g. "20-24"
    age: int                           # e.g. 22
    display_name: str                  # e.g. "Rohan", "Priya", "Maya"
    location: str                      # e.g. "Kathmandu, Nepal", "Delhi, India"
    city: str                          # e.g. "Kathmandu", "Delhi"
    country: str                       # e.g. "Nepal", "India"
    country_code: str                  # e.g. "NP", "IN"
    personality: PersonalityType
    texting_style: TextingStyle
    interests: List[str]
    activity_reason: str               # "just bored tbh", "killing time"
    conversation_confidence: float     # 0.0 to 1.0
    verbosity: VerbosityType
    emoji_tendency: float              # 0.0 to 1.0 probability
    punctuation_tendency: float        # 0.0 to 1.0 probability
    typo_tendency: float               # 0.0 to 0.20 probability
    slang_tendency: float              # 0.0 to 1.0 probability
    double_message_probability: float  # 0.0 to 0.20 probability
    response_delay_profile: DelayProfile
    preferred_conversation_topics: List[str]
    conversation_goals: List[str]
    exit_probability: float            # Per turn termination probability after min turns
    min_exchanges_before_exit: int     # Minimum turns before natural exit is considered
    vocabulary_pool: List[str] = field(default_factory=list)
    age_frozen: Optional[int] = None
    gender_frozen: Optional[str] = None
    name_frozen: Optional[str] = None
    is_synthetic: bool = True          # Mandatory security and separation flag
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.age_frozen is None:
            self.age_frozen = self.age
        if self.gender_frozen is None:
            self.gender_frozen = self.gender
        if self.name_frozen is None:
            self.name_frozen = self.display_name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "synthetic_user_id": self.synthetic_user_id,
            "is_synthetic": True,
            "gender": self.gender,
            "age_range": self.age_range,
            "age": self.age,
            "display_name": self.display_name,
            "location": self.location,
            "city": self.city,
            "country": self.country,
            "country_code": self.country_code,
            "personality": self.personality.value,
            "texting_style": self.texting_style.value,
            "interests": self.interests,
            "activity_reason": self.activity_reason,
            "conversation_confidence": self.conversation_confidence,
            "verbosity": self.verbosity.value,
            "emoji_tendency": self.emoji_tendency,
            "punctuation_tendency": self.punctuation_tendency,
            "typo_tendency": self.typo_tendency,
            "slang_tendency": self.slang_tendency,
            "double_message_probability": self.double_message_probability,
            "response_delay_profile": self.response_delay_profile.value,
            "preferred_conversation_topics": self.preferred_conversation_topics,
            "conversation_goals": self.conversation_goals,
            "exit_probability": self.exit_probability,
            "min_exchanges_before_exit": self.min_exchanges_before_exit,
            "vocabulary_pool": self.vocabulary_pool,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class ConversationMemory:
    conv_id: str
    synthetic_profile: SyntheticProfile
    current_state: ConversationState = ConversationState.INTRO
    user_gender: Optional[str] = None
    user_location: Optional[str] = None
    user_age: Optional[int] = None
    user_interest: Optional[str] = None
    conversation_mood: str = "casual"
    messages_exchanged: int = 0
    synthetic_personality: str = ""
    asked_questions: List[str] = field(default_factory=list)
    shared_facts: List[str] = field(default_factory=list)
    recent_intents: List[str] = field(default_factory=list)
    recent_synthetic_replies: List[str] = field(default_factory=list)
    recent_user_messages: List[str] = field(default_factory=list)
    greeting_sent: bool = False
    last_processed_message_id: Optional[int] = None
    processed_message_ids: Set[int] = field(default_factory=set)
    last_question_asked_by_bot: Optional[str] = None
    current_topic: str = "general"
    last_response_category: Optional[str] = None
    is_active: bool = True
    cancellation_requested: bool = False
    has_ended: bool = False
    ended_reason: Optional[str] = None
    is_synthetic: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    def remember_user_fact(self, key: str, value: Any):
        if key == "user_gender" and value:
            self.user_gender = str(value).lower()
            self.shared_facts.append(f"user_gender:{self.user_gender}")
        elif key == "user_location" and value:
            self.user_location = str(value)
            self.shared_facts.append(f"user_location:{self.user_location}")
        elif key == "user_age" and value:
            self.user_age = int(value)
            self.shared_facts.append(f"user_age:{self.user_age}")
        elif key == "user_interest" and value:
            self.user_interest = str(value)
            self.shared_facts.append(f"user_interest:{self.user_interest}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conv_id": self.conv_id,
            "is_synthetic": True,
            "current_state": self.current_state.value,
            "user_gender": self.user_gender,
            "user_location": self.user_location,
            "user_age": self.user_age,
            "user_interest": self.user_interest,
            "conversation_mood": self.conversation_mood,
            "messages_exchanged": self.messages_exchanged,
            "synthetic_personality": self.synthetic_personality,
            "asked_questions": self.asked_questions,
            "shared_facts": self.shared_facts,
            "has_ended": self.has_ended,
            "ended_reason": self.ended_reason,
            "synthetic_user_id": self.synthetic_profile.synthetic_user_id,
        }


@dataclass
class DialogueResponse:
    text: str
    delay_seconds: float
    is_double_message: bool = False
    second_message_text: Optional[str] = None
    second_message_delay: Optional[float] = None
    state_after: ConversationState = ConversationState.CASUAL_CHAT
    should_end_conversation: bool = False
    debug_notes: Dict[str, Any] = field(default_factory=dict)
