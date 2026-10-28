"""
Synthetic Profile Generator.
Generates human-like synthetic profiles with balanced ~50/50 gender distribution,
distinct personalities, texting nuances, and configurable randomness.
"""

import random
from typing import Dict, List, Optional
from datestranger.synthetic.models import (
    SyntheticProfile,
    PersonalityType,
    TextingStyle,
    VerbosityType,
    DelayProfile,
)

# Realistic names catalog
MALE_NAMES = [
    "Aarav", "Rohan", "Alex", "Samir", "Liam", "Ayush", "Kevin", "Jake",
    "Marcus", "Kiran", "Nikhil", "David", "Lucas", "Bikash", "Prashant",
    "Chris", "Aditya", "Daniel", "Suman", "Leo", "Siddharth", "Ryan",
    "Anish", "Manish", "Gaurav", "Jason", "Bijay", "Ethan", "Arjun", "Ashish"
]

FEMALE_NAMES = [
    "Priya", "Ananya", "Maya", "Sarah", "Elena", "Chloe", "Emily", "Neha",
    "Sofia", "Pooja", "Shreya", "Mia", "Aastha", "Jessica", "Aarti",
    "Rhea", "Alina", "Sita", "Kavya", "Deepa", "Hannah", "Sneha",
    "Tara", "Bipana", "Zoe", "Samikshya", "Anushka", "Nisha", "Ritu", "Lily"
]

LOCATIONS = [
    {"city": "Kathmandu", "country": "Nepal", "country_code": "NP"},
    {"city": "Pokhara", "country": "Nepal", "country_code": "NP"},
    {"city": "Lalitpur", "country": "Nepal", "country_code": "NP"},
    {"city": "Hetauda", "country": "Nepal", "country_code": "NP"},
    {"city": "Biratnagar", "country": "Nepal", "country_code": "NP"},
    {"city": "Butwal", "country": "Nepal", "country_code": "NP"},
    {"city": "Dharan", "country": "Nepal", "country_code": "NP"},
    {"city": "Delhi", "country": "India", "country_code": "IN"},
    {"city": "Mumbai", "country": "India", "country_code": "IN"},
    {"city": "Bangalore", "country": "India", "country_code": "IN"},
    {"city": "Kolkata", "country": "India", "country_code": "IN"},
    {"city": "Pune", "country": "India", "country_code": "IN"},
    {"city": "London", "country": "UK", "country_code": "GB"},
    {"city": "New York", "country": "USA", "country_code": "US"},
    {"city": "Toronto", "country": "Canada", "country_code": "CA"},
    {"city": "Sydney", "country": "Australia", "country_code": "AU"},
]

ACTIVITY_REASONS = [
    "just bored tbh",
    "couldn't sleep",
    "killing time between classes",
    "wanted to see who's around",
    "random chats to pass time",
    "just chilling after work",
    "friends are asleep lol",
    "looking for cool people to chat with",
    "curious how this works haha",
]

INTEREST_SETS = [
    ["gaming", "music", "late night talks"],
    ["movies", "anime", "drawing"],
    ["travel", "photography", "indie songs"],
    ["football", "gym", "music"],
    ["coding", "podcasts", "coffee"],
    ["reading", "lofi beats", "scrolling tiktok"],
    ["cooking", "memes", "random facts"],
    ["netflix", "sleeping", "biking"],
]

# Personality Archetype Configurations
PERSONALITY_CONFIGS: Dict[PersonalityType, Dict] = {
    PersonalityType.CASUAL: {
        "texting_style": TextingStyle.LOWERCASE,
        "verbosity": VerbosityType.SHORT,
        "emoji_tendency": 0.25,
        "punctuation_tendency": 0.20,
        "typo_tendency": 0.05,
        "slang_tendency": 0.65,
        "double_message_probability": 0.08,
        "response_delay_profile": DelayProfile.NORMAL,
        "confidence": 0.70,
        "exit_probability": 0.05,
        "min_exchanges": 8,
        "vocab": ["yo", "sup", "yeah", "nah", "tbh", "same", "cool", "lol", "rn"],
    },
    PersonalityType.FRIENDLY: {
        "texting_style": TextingStyle.EXPRESSIVE,
        "verbosity": VerbosityType.MEDIUM,
        "emoji_tendency": 0.55,
        "punctuation_tendency": 0.60,
        "typo_tendency": 0.03,
        "slang_tendency": 0.35,
        "double_message_probability": 0.12,
        "response_delay_profile": DelayProfile.FAST,
        "confidence": 0.85,
        "exit_probability": 0.03,
        "min_exchanges": 12,
        "vocab": ["hey haha", "nice", "awesome", "aww", "glad to hear", "how's your day", "haha"],
    },
    PersonalityType.SHY: {
        "texting_style": TextingStyle.LOWERCASE,
        "verbosity": VerbosityType.VERY_SHORT,
        "emoji_tendency": 0.30,
        "punctuation_tendency": 0.15,
        "typo_tendency": 0.04,
        "slang_tendency": 0.30,
        "double_message_probability": 0.04,
        "response_delay_profile": DelayProfile.SLOW,
        "confidence": 0.35,
        "exit_probability": 0.06,
        "min_exchanges": 7,
        "vocab": ["hey", "uhh", "kinda", "idk lol", "not sure", "sorry", "lol", "😭"],
    },
    PersonalityType.DIRECT: {
        "texting_style": TextingStyle.MINIMAL,
        "verbosity": VerbosityType.VERY_SHORT,
        "emoji_tendency": 0.08,
        "punctuation_tendency": 0.30,
        "typo_tendency": 0.02,
        "slang_tendency": 0.40,
        "double_message_probability": 0.05,
        "response_delay_profile": DelayProfile.FAST,
        "confidence": 0.90,
        "exit_probability": 0.07,
        "min_exchanges": 6,
        "vocab": ["hey", "m or f", "u?", "from?", "what are you looking for", "k", "yup"],
    },
    PersonalityType.BORED: {
        "texting_style": TextingStyle.LOWERCASE,
        "verbosity": VerbosityType.SHORT,
        "emoji_tendency": 0.15,
        "punctuation_tendency": 0.10,
        "typo_tendency": 0.06,
        "slang_tendency": 0.50,
        "double_message_probability": 0.06,
        "response_delay_profile": DelayProfile.INCONSISTENT,
        "confidence": 0.50,
        "exit_probability": 0.06,
        "min_exchanges": 6,
        "vocab": ["bored tbh", "meh", "nothing much", "u?", "same", "killing time", "idk"],
    },
    PersonalityType.CURIOUS: {
        "texting_style": TextingStyle.CASUAL_SLANG,
        "verbosity": VerbosityType.MEDIUM,
        "emoji_tendency": 0.35,
        "punctuation_tendency": 0.45,
        "typo_tendency": 0.03,
        "slang_tendency": 0.45,
        "double_message_probability": 0.10,
        "response_delay_profile": DelayProfile.NORMAL,
        "confidence": 0.80,
        "exit_probability": 0.04,
        "min_exchanges": 10,
        "vocab": ["oh really?", "where at?", "tell me", "what do you do", "wait why", "nice"],
    },
    PersonalityType.DRY_TEXTER: {
        "texting_style": TextingStyle.MINIMAL,
        "verbosity": VerbosityType.VERY_SHORT,
        "emoji_tendency": 0.05,
        "punctuation_tendency": 0.05,
        "typo_tendency": 0.03,
        "slang_tendency": 0.20,
        "double_message_probability": 0.02,
        "response_delay_profile": DelayProfile.SLOW,
        "confidence": 0.40,
        "exit_probability": 0.08,
        "min_exchanges": 5,
        "vocab": ["hey", "good", "you?", "k", "nice", "yea", "cool", "nah"],
    },
    PersonalityType.ENERGETIC: {
        "texting_style": TextingStyle.EXPRESSIVE,
        "verbosity": VerbosityType.MEDIUM,
        "emoji_tendency": 0.70,
        "punctuation_tendency": 0.30,
        "typo_tendency": 0.08,
        "slang_tendency": 0.75,
        "double_message_probability": 0.18,
        "response_delay_profile": DelayProfile.FAST,
        "confidence": 0.95,
        "exit_probability": 0.02,
        "min_exchanges": 12,
        "vocab": ["heyy 😂", "omg", "fr", "ngl", "lmao", "yooo", "no way", "haha"],
    },
    PersonalityType.SLIGHTLY_AWKWARD: {
        "texting_style": TextingStyle.LOWERCASE,
        "verbosity": VerbosityType.SHORT,
        "emoji_tendency": 0.25,
        "punctuation_tendency": 0.25,
        "typo_tendency": 0.05,
        "slang_tendency": 0.35,
        "double_message_probability": 0.07,
        "response_delay_profile": DelayProfile.INCONSISTENT,
        "confidence": 0.45,
        "exit_probability": 0.05,
        "min_exchanges": 7,
        "vocab": ["uhh hi lol", "i have no idea", "kinda awkward", "haha my bad", "oof", "😅"],
    },
    PersonalityType.QUIET: {
        "texting_style": TextingStyle.MINIMAL,
        "verbosity": VerbosityType.VERY_SHORT,
        "emoji_tendency": 0.10,
        "punctuation_tendency": 0.10,
        "typo_tendency": 0.02,
        "slang_tendency": 0.25,
        "double_message_probability": 0.03,
        "response_delay_profile": DelayProfile.SLOW,
        "confidence": 0.30,
        "exit_probability": 0.08,
        "min_exchanges": 5,
        "vocab": ["yeah", "maybe", "idk", "haha", "cool", "hmm"],
    },
}


class SyntheticProfileGenerator:
    """
    Generates synthetic profiles with configurable probabilities and realistic variations.
    """

    def __init__(self, male_weight: float = 0.50, female_weight: float = 0.50, seed: Optional[int] = None):
        self.male_weight = male_weight
        self.female_weight = female_weight
        self.rng = random.Random(seed) if seed is not None else random.Random()
        self._next_id = 900000001

    def generate(
        self,
        preferred_gender: Optional[str] = None,
        preferred_personality: Optional[PersonalityType] = None,
        custom_id: Optional[int] = None,
    ) -> SyntheticProfile:
        # Determine gender based on preference or weighted 50/50 randomness
        if preferred_gender and preferred_gender.lower() in ["male", "female"]:
            gender = preferred_gender.lower()
        else:
            # Weighted random choice with small natural jitter
            gender = self.rng.choices(
                ["male", "female"],
                weights=[self.male_weight, self.female_weight],
                k=1
            )[0]

        # Name selection
        if gender == "male":
            name = self.rng.choice(MALE_NAMES)
        else:
            name = self.rng.choice(FEMALE_NAMES)

        # Location selection
        loc_data = self.rng.choice(LOCATIONS)
        city = loc_data["city"]
        country = loc_data["country"]
        country_code = loc_data["country_code"]
        location_str = f"{city}, {country}"

        # Personality archetype
        if preferred_personality:
            personality = preferred_personality
        else:
            personality = self.rng.choice(list(PersonalityType))

        p_cfg = PERSONALITY_CONFIGS[personality]

        # Age and Age Range
        age = self.rng.randint(19, 29)
        if age <= 22:
            age_range = "18-22"
        elif age <= 25:
            age_range = "22-25"
        else:
            age_range = "26-30"

        # Unique synthetic ID in the reserved range 900_000_000 - 999_999_999
        if custom_id is not None:
            synth_id = custom_id
        else:
            synth_id = self.rng.randint(900000100, 999999000)

        interests = self.rng.choice(INTEREST_SETS)
        activity_reason = self.rng.choice(ACTIVITY_REASONS)

        # Apply minor variation jitter to tendencies
        emoji_tendency = max(0.0, min(0.9, p_cfg["emoji_tendency"] + self.rng.uniform(-0.05, 0.05)))
        punctuation_tendency = max(0.0, min(0.9, p_cfg["punctuation_tendency"] + self.rng.uniform(-0.05, 0.05)))
        typo_tendency = max(0.01, min(0.15, p_cfg["typo_tendency"] + self.rng.uniform(-0.01, 0.02)))
        slang_tendency = max(0.1, min(0.9, p_cfg["slang_tendency"] + self.rng.uniform(-0.05, 0.05)))
        exit_probability = max(0.03, min(0.35, p_cfg["exit_probability"] + self.rng.uniform(-0.02, 0.03)))

        return SyntheticProfile(
            synthetic_user_id=synth_id,
            gender=gender,
            age_range=age_range,
            age=age,
            display_name=name,
            location=location_str,
            city=city,
            country=country,
            country_code=country_code,
            personality=personality,
            texting_style=p_cfg["texting_style"],
            interests=interests,
            activity_reason=activity_reason,
            conversation_confidence=p_cfg["confidence"],
            verbosity=p_cfg["verbosity"],
            emoji_tendency=emoji_tendency,
            punctuation_tendency=punctuation_tendency,
            typo_tendency=typo_tendency,
            slang_tendency=slang_tendency,
            double_message_probability=p_cfg["double_message_probability"],
            response_delay_profile=p_cfg["response_delay_profile"],
            preferred_conversation_topics=["casual", "location", "daily life", "hobbies"],
            conversation_goals=["pass time", "friendly chat"],
            exit_probability=exit_probability,
            min_exchanges_before_exit=p_cfg["min_exchanges"],
            vocabulary_pool=p_cfg["vocab"],
            age_frozen=age,
            gender_frozen=gender,
            name_frozen=name,
            is_synthetic=True,
        )
