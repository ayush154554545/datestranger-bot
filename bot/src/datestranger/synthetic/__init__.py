"""
DateStranger Synthetic Conversation Engine Package.
A controlled, non-deceptive synthetic user engine for testing, onboarding, and empty-state demos.
"""

from datestranger.synthetic.models import (
    SyntheticMode,
    PersonalityType,
    TextingStyle,
    VerbosityType,
    DelayProfile,
    ConversationState,
    UserIntent,
    SyntheticProfile,
    ConversationMemory,
    DialogueResponse,
)
from datestranger.synthetic.generator import SyntheticProfileGenerator
from datestranger.synthetic.classifier import IntentClassifier
from datestranger.synthetic.memory import ConversationMemoryManager
from datestranger.synthetic.state_machine import ConversationStateMachine
from datestranger.synthetic.anti_repetition import AntiRepetitionEngine
from datestranger.synthetic.variation_engine import VariationEngine
from datestranger.synthetic.timing_engine import TimingEngine
from datestranger.synthetic.response_selector import ResponseSelector
from datestranger.synthetic.demo_manager import DemoManager
from datestranger.synthetic.engine import SyntheticConversationEngine

__all__ = [
    "SyntheticMode",
    "PersonalityType",
    "TextingStyle",
    "VerbosityType",
    "DelayProfile",
    "ConversationState",
    "UserIntent",
    "SyntheticProfile",
    "ConversationMemory",
    "DialogueResponse",
    "SyntheticProfileGenerator",
    "IntentClassifier",
    "ConversationMemoryManager",
    "ConversationStateMachine",
    "AntiRepetitionEngine",
    "VariationEngine",
    "TimingEngine",
    "ResponseSelector",
    "DemoManager",
    "SyntheticConversationEngine",
]
