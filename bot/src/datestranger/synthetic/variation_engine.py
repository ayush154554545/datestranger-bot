"""
Variation Engine.
Applies profile-specific texting styles, casing, punctuation removal,
controlled typos, slang variations, and emojis.
"""

import random
import re
from typing import Optional
from datestranger.synthetic.models import SyntheticProfile, TextingStyle


# Common realistic typing substitutions and typos
TYPO_MAP = {
    "the": ["teh", "th"],
    "you": ["u", "yu"],
    "your": ["ur", "yor"],
    "you're": ["ur", "youre"],
    "what's": ["whats", "wats"],
    "what": ["wat", "wht"],
    "with": ["wit", "wid"],
    "i'm": ["im", "i am"],
    "just": ["jst", "jus"],
    "because": ["cuz", "bc"],
    "really": ["realy", "rly"],
    "about": ["abt", "abou"],
    "people": ["ppl", "peopl"],
    "nothing": ["nothin", "nth"],
}

SLANG_MAP = {
    "to be honest": "tbh",
    "not gonna lie": "ngl",
    "for real": "fr",
    "right now": "rn",
    "by the way": "btw",
    "i don't know": "idk",
}

AVAILABLE_EMOJIS = ["😂", "😭", "😅", "🙂", "👀", "✨", "🙌", "💀"]


class VariationEngine:
    """
    Renders draft templates into realistic human text reflecting the profile's
    texting style, typos, slang, casing, and emoji frequency.
    """

    def __init__(self, rng: Optional[random.Random] = None):
        self.rng = rng or random.Random()

    def apply_style(self, text: str, profile: SyntheticProfile) -> str:
        res = text

        # 1. Template variable substitutions
        synth_name = getattr(profile, "name_frozen", None) or profile.display_name
        synth_age = getattr(profile, "age_frozen", None) or profile.age
        res = res.replace("{synth_name}", synth_name)
        res = res.replace("{synth_city}", profile.city)
        res = res.replace("{synth_country}", profile.country)
        res = res.replace("{synth_location}", profile.location)
        res = res.replace("{synth_age}", str(synth_age))
        res = res.replace("{synth_activity}", profile.activity_reason)

        # 2. Slang substitutions based on profile.slang_tendency
        if self.rng.random() < profile.slang_tendency:
            for full_phrase, slang in SLANG_MAP.items():
                if full_phrase in res.lower():
                    # Case-insensitive replacement
                    pattern = re.compile(re.escape(full_phrase), re.IGNORECASE)
                    res = pattern.sub(slang, res)

        # 3. Controlled Typos based on profile.typo_tendency
        if self.rng.random() < profile.typo_tendency:
            words = res.split()
            new_words = []
            applied_typo = False
            for w in words:
                clean_w = w.lower().strip(".,!?")
                if not applied_typo and clean_w in TYPO_MAP and self.rng.random() < 0.50:
                    replacement = self.rng.choice(TYPO_MAP[clean_w])
                    # Preserve punctuation if any
                    trailing = ""
                    if w and w[-1] in ".,!?":
                        trailing = w[-1]
                    new_words.append(replacement + trailing)
                    applied_typo = True
                else:
                    new_words.append(w)
            res = " ".join(new_words)

        # 4. Casing and punctuation handling
        if profile.texting_style in [TextingStyle.LOWERCASE, TextingStyle.MINIMAL]:
            res = res.lower()
            if self.rng.random() > profile.punctuation_tendency:
                # Strip ending periods
                if res.endswith("."):
                    res = res[:-1]
        elif profile.texting_style == TextingStyle.PUNCTUATED:
            # Capitalize first letter
            if res and res[0].islower():
                res = res[0].upper() + res[1:]

        # 5. Emoji attachment based on emoji_tendency
        # Don't add emojis if message already has emojis
        has_existing_emoji = any(c in res for c in AVAILABLE_EMOJIS)
        if not has_existing_emoji and self.rng.random() < profile.emoji_tendency:
            chosen_emoji = self.rng.choice(AVAILABLE_EMOJIS)
            # Friendly/Energetic gets 😂 or 🙂, Shy gets 😭 or 😅
            if profile.personality.value in ["SHY", "SLIGHTLY_AWKWARD"]:
                chosen_emoji = self.rng.choice(["😭", "😅", "lol"])
            elif profile.personality.value in ["ENERGETIC"]:
                chosen_emoji = self.rng.choice(["😂", "💀", "😭"])
            elif profile.personality.value in ["FRIENDLY"]:
                chosen_emoji = self.rng.choice(["🙂", "✨", "haha"])

            if chosen_emoji in ["lol", "haha"]:
                res = f"{res} {chosen_emoji}"
            else:
                res = f"{res} {chosen_emoji}"

        return res.strip()
