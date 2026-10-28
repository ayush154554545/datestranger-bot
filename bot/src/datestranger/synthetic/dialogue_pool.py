"""
Dialogue Pool & Templates.
Hundreds of human-sounding conversational branches, reactions, statements,
questions, and endings. Strictly free of AI-like generic canned phrases.
"""

from typing import Dict, List, Optional
from datestranger.synthetic.models import PersonalityType, ConversationState, UserIntent

# Opening Messages by Personality Archetype
OPENINGS_BY_PERSONALITY: Dict[PersonalityType, List[Dict]] = {
    PersonalityType.CASUAL: [
        {"text": "hey", "delay": 2.2},
        {"text": "yo", "delay": 1.8},
        {"text": "sup", "delay": 2.0},
        {"text": "heyy", "delay": 2.5},
        {"text": "hey, what's up?", "delay": 3.0},
        {"text": "yo, anyone here?", "delay": 2.8},
    ],
    PersonalityType.FRIENDLY: [
        {"text": "hey haha, how's your day going?", "delay": 3.2},
        {"text": "heyy! what brings you here?", "delay": 3.5},
        {"text": "hi there! how are you?", "delay": 2.8},
        {"text": "hey! hope your day is going well 🙂", "delay": 3.4},
        {"text": "heyy, glad we matched haha", "delay": 3.0},
    ],
    PersonalityType.SHY: [
        {"text": "hey", "delay": 4.5},
        {"text": "hi..", "delay": 5.0},
        {"text": "im kinda new here lol", "delay": 5.2},
        {"text": "hey, not really sure what to say 😭", "delay": 6.0},
        {"text": "uh hi lol", "delay": 4.8},
    ],
    PersonalityType.DIRECT: [
        {"text": "hey", "delay": 1.5},
        {"text": "m or f?", "delay": 1.8},
        {"text": "what are you looking for?", "delay": 2.2},
        {"text": "yo, where u from?", "delay": 2.0},
        {"text": "hey, what's good", "delay": 1.9},
    ],
    PersonalityType.BORED: [
        {"text": "hey", "delay": 3.0},
        {"text": "just bored tbh", "delay": 3.5},
        {"text": "heyy", "delay": 2.8},
        {"text": "so bored rn lol", "delay": 3.2},
        {"text": "anyone awake?", "delay": 3.8},
    ],
    PersonalityType.CURIOUS: [
        {"text": "hey, where are you from?", "delay": 2.8},
        {"text": "what's up! what do you usually do here?", "delay": 3.2},
        {"text": "heyy, you from around here?", "delay": 3.0},
        {"text": "hey! what brings u here today?", "delay": 2.7},
    ],
    PersonalityType.DRY_TEXTER: [
        {"text": "hey", "delay": 4.0},
        {"text": "hi", "delay": 4.5},
        {"text": "sup", "delay": 3.5},
        {"text": "yo", "delay": 4.2},
    ],
    PersonalityType.ENERGETIC: [
        {"text": "heyy 😂", "delay": 2.0},
        {"text": "what's up!", "delay": 1.8},
        {"text": "yooo how's it going?", "delay": 2.2},
        {"text": "heyyy! what's good?", "delay": 2.5},
    ],
    PersonalityType.SLIGHTLY_AWKWARD: [
        {"text": "hey", "delay": 3.8},
        {"text": "uhh hi lol", "delay": 4.2},
        {"text": "i have no idea how to start this haha", "delay": 4.5},
        {"text": "hi! awkward silence in 3.. 2.. 1.. 😂", "delay": 4.0},
    ],
    PersonalityType.QUIET: [
        {"text": "hey", "delay": 5.5},
        {"text": "hi", "delay": 6.0},
        {"text": "hello", "delay": 5.0},
    ],
}

# ============================================================
# DIRECT INQUIRY RESPONSES (Answering user questions directly)
# ============================================================

# When user asks: "how are you?", "how r u", "how's it going", "and u"
HOW_ARE_YOU_REPLIES: List[Dict] = [
    {"text": "im good haha, how are you?", "weight": 0.30},
    {"text": "pretty good, just chilling rn! u?", "weight": 0.25},
    {"text": "doing well 🙂 how about you?", "weight": 0.20},
    {"text": "good! how's your day going so far?", "weight": 0.15},
    {"text": "a bit tired tbh lol, what about you?", "weight": 0.10},
]

# When user asks: "your name?", "name?", "who are you"
NAME_DISCLOSURES: List[Dict] = [
    {"text": "im {synth_name} haha, u?", "weight": 0.35},
    {"text": "{synth_name}, what's your name?", "weight": 0.25},
    {"text": "{synth_name}! what about you?", "weight": 0.25},
    {"text": "call me {synth_name} haha, u?", "weight": 0.15},
]

# When user asks: "where are you from?", "from?", "location?"
SYNTHETIC_LOCATION_DISCLOSURES: List[Dict] = [
    {"text": "from {synth_city}, u?", "weight": 0.30},
    {"text": "{synth_country}, what about you?", "weight": 0.25},
    {"text": "im in {synth_city} rn, where are you from?", "weight": 0.25},
    {"text": "{synth_location}! you?", "weight": 0.20},
]

# When user asks: "how old are you?", "age?"
AGE_DISCLOSURES: List[Dict] = [
    {"text": "im {synth_age} haha, u?", "weight": 0.35},
    {"text": "{synth_age}, what about you?", "weight": 0.30},
    {"text": "{synth_age}! u?", "weight": 0.25},
    {"text": "turned {synth_age} recently lol, you?", "weight": 0.10},
]

# When user asks: "m or f?", "gender?", "boy or girl"
GENDER_DISCLOSURES_FEMALE: List[Dict] = [
    {"text": "f haha, u?", "weight": 0.35},
    {"text": "girl here, you?", "weight": 0.30},
    {"text": "f! what about you?", "weight": 0.20},
    {"text": "female, u?", "weight": 0.15},
]

GENDER_DISCLOSURES_MALE: List[Dict] = [
    {"text": "m bro, u?", "weight": 0.35},
    {"text": "guy here haha, you?", "weight": 0.30},
    {"text": "m! what about you?", "weight": 0.20},
    {"text": "male, u?", "weight": 0.15},
]

# When user asks: "what brings you here?", "why are you here?"
REASON_DISCLOSURES: List[Dict] = [
    {"text": "honestly just bored lol, what about you?", "weight": 0.35},
    {"text": "{synth_activity}, u?", "weight": 0.25},
    {"text": "just looking for chill chats haha, what brings u here?", "weight": 0.25},
    {"text": "couldn't sleep tbh haha, you?", "weight": 0.15},
]

# When user asks: "what are you doing?", "wyd?"
DOING_DISCLOSURES: List[Dict] = [
    {"text": "just listening to music and laying in bed haha, u?", "weight": 0.30},
    {"text": "scrolling on my phone tbh lol, you?", "weight": 0.25},
    {"text": "watching random videos, what about you?", "weight": 0.25},
    {"text": "nothing much, just chilling rn. u?", "weight": 0.20},
]

# When user asks: "are u mad?", "are you angry?"
CHALLENGE_MAD_REPLIES: List[Dict] = [
    {"text": "lmao no why would i be mad 😂", "weight": 0.35},
    {"text": "nah not at all haha, why?", "weight": 0.30},
    {"text": "lol no, did i sound mad?", "weight": 0.20},
    {"text": "haha no why 😂 everything good?", "weight": 0.15},
]

# When user asks: "are you a bot?", "bot?", "are u real?"
CHALLENGE_BOT_REPLIES: List[Dict] = [
    {"text": "lmao nah im real 😂", "weight": 0.35},
    {"text": "bro what, no haha", "weight": 0.25},
    {"text": "why does everyone ask that lol, definitely real", "weight": 0.25},
    {"text": "haha no, are you? 😂", "weight": 0.15},
]

# When user expresses confusion: "what?", "huh?", "wdym?"
CONFUSION_REPLIES: List[Dict] = [
    {"text": "haha what did i say lol", "weight": 0.30},
    {"text": "wait what did u mean haha", "weight": 0.25},
    {"text": "huh? what lol", "weight": 0.25},
    {"text": "nothing nothing haha, all good", "weight": 0.20},
]

# Contextual responses to user saying "no" / "nah"
ANSWER_NO_REACTIONS: List[Dict] = [
    {"text": "fair enough haha", "weight": 0.30},
    {"text": "oh okay lol", "weight": 0.25},
    {"text": "what do u usually do then?", "weight": 0.25, "asks": "activity"},
    {"text": "ah gotchu haha", "weight": 0.20},
]

# Contextual responses to user saying "yes" / "yeah"
ANSWER_YES_REACTIONS: List[Dict] = [
    {"text": "nice haha", "weight": 0.30},
    {"text": "oh cool!", "weight": 0.25},
    {"text": "haha yeah totally", "weight": 0.25},
    {"text": "same here tbh", "weight": 0.20},
]

# Contextual responses to user saying "nothing" / "not much"
ANSWER_NOTHING_REACTIONS: List[Dict] = [
    {"text": "same honestly, pretty quiet day today", "weight": 0.35},
    {"text": "haha felt that, boredom hits hard lol", "weight": 0.30},
    {"text": "yeah honestly same, just scrolling", "weight": 0.35},
]

# Contextual responses to user saying "idk" / unknown answer to questions
UNKNOWN_ANSWER_REACTIONS: List[Dict] = [
    {"text": "haha fair enough, keeping it a mystery 😂", "weight": 0.35},
    {"text": "lol all good, no worries 🙂", "weight": 0.35},
    {"text": "haha secret huh? fair enough lol", "weight": 0.30},
]

# General greeting responses when user says "hi" / "hello"
GREETING_REPLIES: List[Dict] = [
    {"text": "heyy haha", "weight": 0.30},
    {"text": "hey! how's it going?", "weight": 0.30},
    {"text": "heyy 🙂 what's up?", "weight": 0.25},
    {"text": "yo! how are you doing?", "weight": 0.15},
]

# Acknowledgments for user answers to bot's previous questions (Without repeating questions!)
LOCATION_ANSWER_ACKNOWLEDGMENTS: List[Dict] = [
    {"text": "oh nice, never been there haha", "weight": 0.35},
    {"text": "cool haha, pretty far from {synth_city}", "weight": 0.25},
    {"text": "nice haha, always wanted to visit", "weight": 0.25},
    {"text": "oh really? how's the weather there rn?", "weight": 0.15},
]

ACTIVITY_ANSWER_ACKNOWLEDGMENTS: List[Dict] = [
    {"text": "oh nice haha, sounds chill", "weight": 0.35},
    {"text": "fair enough lol, pretty quiet day today", "weight": 0.30},
    {"text": "cool! i'm mostly just scrolling on my phone tbh lol", "weight": 0.25},
    {"text": "haha felt that, just chilling is the best", "weight": 0.10},
]

MUSIC_ANSWER_ACKNOWLEDGMENTS: List[Dict] = [
    {"text": "good taste haha", "weight": 0.35},
    {"text": "oh nice! i listen to a bit of everything tbh lol", "weight": 0.35},
    {"text": "dope, definitely gonna check that out", "weight": 0.30},
]

# Gender Disclosures when User states their gender
GENDER_REPLIES: Dict[str, List[Dict]] = {
    "user_male_synthetic_female": [
        {"text": "ohh hey 😂 girl here", "weight": 0.30},
        {"text": "haha hey, f here", "weight": 0.25},
        {"text": "nice, female here! where u from?", "weight": 0.20, "asks": "location"},
        {"text": "hey 😂 same, just bored. girl here btw", "weight": 0.15},
        {"text": "f here! what brings u here?", "weight": 0.10, "asks": "reason"},
    ],
    "user_male_synthetic_male": [
        {"text": "yo bro, guy here too", "weight": 0.30},
        {"text": "haha hey dude, m here", "weight": 0.25},
        {"text": "sup man! just looking for chill chats?", "weight": 0.25},
        {"text": "yo! where u from bro?", "weight": 0.20, "asks": "location"},
    ],
    "user_female_synthetic_male": [
        {"text": "oh hey! guy here haha", "weight": 0.30},
        {"text": "heyy 🙂 m here. how's your day going?", "weight": 0.25},
        {"text": "nice to meet u, m here! where u from?", "weight": 0.25, "asks": "location"},
        {"text": "haha hey! what brings u here?", "weight": 0.20, "asks": "reason"},
    ],
    "user_female_synthetic_female": [
        {"text": "omg girl hey!! 😂", "weight": 0.35},
        {"text": "heyy haha f here too!", "weight": 0.30},
        {"text": "rare to find another girl here lol, where u from?", "weight": 0.25, "asks": "location"},
        {"text": "heyy 🙂 how are you doing today?", "weight": 0.10},
    ],
}

# Location Exchanges (When user shares their location)
LOCATION_REPLIES: List[Dict] = [
    {"text": "ohh nice! {synth_location}, u?", "weight": 0.25},
    {"text": "cool haha, i'm from {synth_city}", "weight": 0.20},
    {"text": "oh nice, never been there tho", "weight": 0.18},
    {"text": "nice! pretty far from {synth_city} haha", "weight": 0.15},
    {"text": "oh really? how's the weather there rn?", "weight": 0.12},
    {"text": "nice haha, always wanted to visit", "weight": 0.10},
]

# Boredom / Casual Chat Exchanges
BOREDOM_REPLIES: List[Dict] = [
    {"text": "same honestly 😂", "weight": 0.25},
    {"text": "haha just killing time tbh", "weight": 0.20},
    {"text": "honestly? just bored lol", "weight": 0.20},
    {"text": "fr, nothing good to do rn", "weight": 0.15},
    {"text": "same here, what are u up to besides this?", "weight": 0.10, "asks": "activity"},
    {"text": "yeah pretty quiet day today", "weight": 0.10},
]

# Short User Replies Reactions ("k", "lol", "same", "yeah")
SHORT_REPLY_REACTIONS: Dict[PersonalityType, List[Dict]] = {
    PersonalityType.CASUAL: [
        {"text": "haha yeah", "weight": 0.30},
        {"text": "fr 😂", "weight": 0.25},
        {"text": "so what u doing rn?", "weight": 0.25, "asks": "activity"},
        {"text": "fair enough", "weight": 0.20},
    ],
    PersonalityType.FRIENDLY: [
        {"text": "haha totally! anything fun planned for today?", "weight": 0.40, "asks": "plans"},
        {"text": "nice haha, how was the rest of your week?", "weight": 0.30, "asks": "week"},
        {"text": "glad to hear 😊", "weight": 0.30},
    ],
    PersonalityType.SHY: [
        {"text": "yeah lol", "weight": 0.40},
        {"text": "haha..", "weight": 0.30},
        {"text": "not really sure what else to say 😭", "weight": 0.30},
    ],
    PersonalityType.DIRECT: [
        {"text": "cool", "weight": 0.35},
        {"text": "where u from?", "weight": 0.35, "asks": "location"},
        {"text": "you looking for someone specific?", "weight": 0.30, "asks": "intent"},
    ],
    PersonalityType.BORED: [
        {"text": "yeah", "weight": 0.40},
        {"text": "pretty dry rn tbh lol", "weight": 0.35},
        {"text": "same here", "weight": 0.25},
    ],
    PersonalityType.DRY_TEXTER: [
        {"text": "k", "weight": 0.40},
        {"text": "cool", "weight": 0.35},
        {"text": "yea", "weight": 0.25},
    ],
    PersonalityType.ENERGETIC: [
        {"text": "haha totally 😂", "weight": 0.35},
        {"text": "what kind of stuff do you usually do?", "weight": 0.35, "asks": "activity"},
        {"text": "haha niceee", "weight": 0.30},
    ],
    PersonalityType.SLIGHTLY_AWKWARD: [
        {"text": "haha yep", "weight": 0.40},
        {"text": "so uhh.. what do you do for fun? lol", "weight": 0.35, "asks": "hobbies"},
        {"text": "did i make it weird already 😂", "weight": 0.25},
    ],
    PersonalityType.QUIET: [
        {"text": "yeah", "weight": 0.50},
        {"text": "idk haha", "weight": 0.30},
        {"text": "hmm", "weight": 0.20},
    ],
    PersonalityType.CURIOUS: [
        {"text": "haha yeah, what music do u usually listen to?", "weight": 0.35, "asks": "music"},
        {"text": "cool, do u stay up late often?", "weight": 0.35, "asks": "habits"},
        {"text": "ohh nice", "weight": 0.30},
    ],
}

# Interest / Hobby Discovery Exchanges
INTEREST_REPLIES: List[Dict] = [
    {"text": "oh nice, what kind of games do u play?", "weight": 0.25, "interest": "gaming"},
    {"text": "cool! who's your favorite artist rn?", "weight": 0.25, "interest": "music"},
    {"text": "same here honestly, seen any good movies recently?", "weight": 0.20, "interest": "movies"},
    {"text": "oh really? that's dope haha", "weight": 0.15},
    {"text": "i mostly just listen to music or scroll when bored lol", "weight": 0.15},
]

# Natural Endings (Terminations)
NATURAL_ENDINGS: List[Dict] = [
    {"text": "anyway gotta go lol, nice talking to u", "weight": 0.25},
    {"text": "im gonna head out, take care!", "weight": 0.25},
    {"text": "gotta go do something rn, catch u later!", "weight": 0.25},
    {"text": "gotta sleep soon, talk later!", "weight": 0.25},
]

# Cohesive Double-Message Pairs
DOUBLE_MESSAGE_PAIRS: List[Dict] = [
    {"first": "wait", "second": "where are you from?", "second_delay": 2.0},
    {"first": "lol", "second": "that's actually funny", "second_delay": 1.8},
    {"first": "haha", "second": "same honestly", "second_delay": 1.5},
    {"first": "wait really?", "second": "i didn't expect that haha", "second_delay": 2.2},
    {"first": "ngl", "second": "it's rare finding someone chill here 😂", "second_delay": 2.4},
]
