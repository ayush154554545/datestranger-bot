"""
Lightweight User Response Classifier.
Detects user intents (single or multi-intent) and extracts conversational entities
(gender, location, age, interest, etc.) to feed conversation memory.
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from datestranger.synthetic.models import UserIntent


class ClassifiedMessage:
    def __init__(
        self,
        raw_text: str,
        intents: List[UserIntent],
        extracted_entities: Dict[str, any],
        is_question: bool = False,
        is_short: bool = False,
        is_long: bool = False,
    ):
        self.raw_text = raw_text
        self.intents = intents
        self.extracted_entities = extracted_entities
        self.is_question = is_question
        self.is_short = is_short
        self.is_long = is_long

    def has_intent(self, intent: UserIntent) -> bool:
        return intent in self.intents

    def primary_intent(self) -> UserIntent:
        if not self.intents:
            return UserIntent.UNKNOWN
        # Specific user inquiries and challenges take precedence over generic replies
        priority_order = [
            UserIntent.COMMAND_STOP,
            UserIntent.BYE,
            UserIntent.DISINTEREST,
            # Direct user questions about synthetic partner
            UserIntent.CHALLENGE_MAD,
            UserIntent.CHALLENGE_BOT,
            UserIntent.CONFUSION,
            UserIntent.ASK_NAME,
            UserIntent.ASK_AGE,
            UserIntent.ASK_GENDER,
            UserIntent.ASK_LOCATION,
            UserIntent.ASK_HOW_ARE_YOU,
            UserIntent.ASK_REASON,
            UserIntent.ASK_DOING,
            # User answers to bot questions
            UserIntent.USER_ANSWER_NO,
            UserIntent.USER_ANSWER_YES,
            UserIntent.USER_ANSWER_NOTHING,
            UserIntent.AGE_UNKNOWN,
            UserIntent.UNKNOWN_ANSWER,
            # User sharing facts about themselves
            UserIntent.GENDER_MALE,
            UserIntent.GENDER_FEMALE,
            UserIntent.LOCATION,
            UserIntent.AGE,
            UserIntent.BORED,
            UserIntent.LOOKING_FOR_FRIENDS,
            UserIntent.LOOKING_FOR_CHAT,
            UserIntent.FLIRTING,
            UserIntent.INTEREST,
            UserIntent.QUESTION,
            UserIntent.GREETING,
            UserIntent.INTRODUCTION,
            UserIntent.POSITIVE,
            UserIntent.NEGATIVE,
            UserIntent.SHORT_REPLY,
            UserIntent.LONG_REPLY,
            UserIntent.UNKNOWN,
        ]
        for p in priority_order:
            if p in self.intents:
                return p
        return self.intents[0]


class IntentClassifier:
    """
    Fast rule-based and regex classifier for natural texting in stranger chat.
    Accurately distinguishes user inquiries, answers, facts, and short reactions.
    """

    COMMAND_STOP_PATTERNS = [
        r"^(?:stop|leave|exit|quit|disconnect|next|end|\/stop|\/next|\/leave)$",
        r"\b(?:stop leave|leave chat|stop chat|end chat|stop talking|next partner|stop leave)\b",
        r"🛑"
    ]

    GREETING_PATTERNS = [
        r"\b(hey+|hi+|heyy+|hello|yo+|sup|hola|namaste|anyone here|anybody|hii+|wassup|what'?s up)\b"
    ]

    # Inquiries asked by the user to the bot
    ASK_HOW_ARE_YOU_PATTERNS = [
        r"\b(how are you|how r u|hru|hows it going|how'?s it going|how you doing|how are things|how was your day|how is your day|and u\??|and you\??|hbu\??|wbu\??)\b"
    ]

    ASK_NAME_PATTERNS = [
        r"\b(what(?:'?s| is) your name|your name\??|ur name\??|name\?|who are you|who r u|whats ur name|what is ur name|may i know your name)\b",
        r"^name\??$",
        r"^your name\??$"
    ]

    ASK_LOCATION_PATTERNS = [
        r"\b(where (?:r|are) (?:u|you)(?: from)?|from\?|where do you live|where do u live|which country|which city|what place|where are you located)\b",
        r"^from\??$",
        r"^where\??$",
        r"^location\??$"
    ]

    ASK_AGE_PATTERNS = [
        r"\b(how old (?:are you|r u)|age\?|ur age\??|your age\??|what(?:'?s| is) your age)\b",
        r"^age\??$"
    ]

    ASK_GENDER_PATTERNS = [
        r"\b(m or f|f or m|male or female|female or male|boy or girl|girl or boy|guy or girl|what(?:'?s| is) your gender|gender\?|ur gender\??|asl)\b",
        r"^m or f\??$",
        r"^gender\??$"
    ]

    ASK_REASON_PATTERNS = [
        r"\b(what brings you(?: here)?|why are you here|why r u here|what are you doing here|what r u doing here|looking for what)\b"
    ]

    ASK_DOING_PATTERNS = [
        r"\b(wyd|what are you doing|what r u doing|what are you doing rn|what r u up to|what are you up to)\b",
        r"^wyd\??$"
    ]

    CHALLENGE_MAD_PATTERNS = [
        r"\b(are (?:u|you) (?:mad|angry|crazy|insane|dumb|stupid|offended))\b"
    ]

    CHALLENGE_BOT_PATTERNS = [
        r"\b(are (?:u|you) (?:a )?(?:bot|ai|robot|fake|real person|real|human or ai|ai or human|human))\b",
        r"\b(human or ai|ai or human|bot or real|real or bot|are you real|are u real)\b",
        r"^(?:bot|ai|robot|npc)\??$"
    ]

    CONFUSION_PATTERNS = [
        r"\b(what\?+|huh\?+|what do you mean|wdym|wut\?+|confused)\b",
        r"^what\??$",
        r"^huh\??$",
        r"^wdym\??$"
    ]

    # Specific user answers
    USER_NO_PATTERNS = [
        r"^(?:no|nah|nope|not really|never|na|n)$",
        r"\b(?:no i'?m not|no im not|nah not really)\b"
    ]

    USER_YES_PATTERNS = [
        r"^(?:yes|yeah|yea|yep|yup|sure|of course|y)$",
        r"\b(?:yeah i do|yes i do|yep definitely)\b"
    ]

    USER_NOTHING_PATTERNS = [
        r"^(?:nothing|not much|nothing much|nth|just chilling|chilling|nm)$"
    ]

    # User disclosing facts about themselves
    GENDER_MALE_PATTERNS = [
        r"\b(male here|boy here|guy here|im a guy|i'?m a guy|i am a guy|i am male|im male|i'm male|\b2[0-9]m\b|\b1[8-9]m\b)\b",
        r"\b(?:male|boy|guy|man|dude)\b",
        r"^(?:m)$"
    ]

    GENDER_FEMALE_PATTERNS = [
        r"\b(female here|girl here|woman here|im a girl|i'?m a girl|i am a girl|i am female|im female|i'm female|\b2[0-9]f\b|\b1[8-9]f\b)\b",
        r"\b(?:female|girl|woman)\b",
        r"^(?:f)$"
    ]

    LOCATION_PATTERNS = [
        r"\b(from|living in|in|located in)\s+([a-zA-Z\s]+)",
        r"\b(nepal|kathmandu|pokhara|hetauda|lalitpur|biratnagar|butwal|dharan|chitwan)\b",
        r"\b(india|delhi|mumbai|bangalore|kolkata|pune|chennai|hyderabad)\b",
        r"\b(usa|uk|canada|australia|germany|london|nyc|toronto)\b",
    ]

    AGE_PATTERNS = [
        r"\b(?:i'?m|im|age|am)\s*([1-9][0-9])\b",
        r"\b([1-9][0-9])\s*(?:yrs|years|yo|yr|m|f)\b",
    ]

    BORED_PATTERNS = [
        r"\b(bored|bore|boring|just bored|killing time|nothing to do|bored rn|bored af|so bored)\b"
    ]

    LOOKING_PATTERNS = [
        r"\b(looking for|wanna find|finding|looking to|want to)\s*(friends|chat|someone|talk|fun|partner|date)\b",
        r"\b(just to chat|just chatting|make friends|casual chat)\b"
    ]

    FLIRTING_PATTERNS = [
        r"\b(cute|hot|sexy|pretty|handsome|kiss|hug|date me|love you|single|ur cute|you'?re cute)\b"
    ]

    QUESTION_PATTERNS = [
        r"\?+",
        r"\b(where (?:r|are) u|where are you|what (?:r|are) u doing|what brings you|how old|m or f|f or m|asl|from\?|u\?|and you\?|what about you|hbu|wbu)\b"
    ]

    SHORT_REPLIES = {
        "k", "ok", "okay", "okk", "cool", "nice", "lol", "haha", "lmao", "good",
        "fine", "same", "same here", "tbh", "idk", "hmm", "hm", "wait", "oh",
        "ohh", "oof", "fr", "ngl", "sup", "yo"
    }

    DISINTEREST_PATTERNS = [
        r"\b(whatever|idc|boring|don'?t care|leave|stop talking|bye|gtg|g2g|gotta go|cya|sleepy|leaving)\b"
    ]

    POSITIVE_PATTERNS = [
        r"\b(great|awesome|sounds good|nice one|haha yeah|love it|sweet|perfect|cool|good)\b"
    ]

    NEGATIVE_PATTERNS = [
        r"\b(bad|sad|terrible|awful|hate|sucks|not good|tired|rough day)\b"
    ]

    BYE_PATTERNS = [
        r"\b(bye|goodbye|cya|gtg|g2g|gotta go|take care|goodnight|gn|see ya|have to go)\b"
    ]

    def classify(
        self,
        text: str,
        prior_messages: Optional[List[str]] = None,
        open_questions: Optional[List[str]] = None,
    ) -> ClassifiedMessage:
        cleaned = text.strip()
        low = cleaned.lower()
        intents: Set[UserIntent] = set()
        entities: Dict[str, any] = {}

        words = low.split()
        is_short = len(words) <= 3
        is_long = len(words) >= 12
        is_question = "?" in text or any(re.search(p, low) for p in self.QUESTION_PATTERNS)

        if is_question:
            intents.add(UserIntent.QUESTION)

        # Context-aware intent resolution based on prior questions asked by bot
        if open_questions:
            try:
                print(f"[CLASSIFY] Input: {text}")
                print(f"[CLASSIFY] Context: {open_questions}")
            except UnicodeEncodeError:
                safe_inp = text.encode("ascii", "replace").decode("ascii")
                print(f"[CLASSIFY] Input: {safe_inp}")
                print(f"[CLASSIFY] Context: {open_questions}")
            last_q = str(open_questions[-1]).lower()
            if "age" in last_q or "how old" in last_q:
                if any(re.search(r"\b" + re.escape(w) + r"\b", low) for w in ["idk", "dont know", "don't know", "no idea", "not sure", "guess", "secret"]):
                    intents.add(UserIntent.AGE_UNKNOWN)
                    intents.add(UserIntent.UNKNOWN_ANSWER)
                m = re.search(r"\b([1-9][0-9])\b", low)
                if m:
                    age_val = int(m.group(1))
                    if 16 <= age_val <= 60:
                        intents.add(UserIntent.AGE)
                        entities["user_age"] = age_val

            elif "location" in last_q or "where" in last_q or "from" in last_q:
                if low in ["from?", "from", "where?", "where", "and u?", "u?"]:
                    intents.add(UserIntent.ASK_LOCATION)
                elif not is_question and len(words) <= 4:
                    clean_loc = cleaned.strip(".,!?")
                    if clean_loc.lower() not in ["hi", "hey", "hello", "good", "fine", "ok", "k"]:
                        intents.add(UserIntent.LOCATION)
                        entities["user_location"] = clean_loc.title()

            elif "gender" in last_q or "m or f" in last_q:
                if re.search(r"\b(m|male|boy|guy|man)\b", low) and "female" not in low and "girl" not in low:
                    intents.add(UserIntent.GENDER_MALE)
                    entities["user_gender"] = "male"
                elif re.search(r"\b(f|female|girl|woman)\b", low):
                    intents.add(UserIntent.GENDER_FEMALE)
                    entities["user_gender"] = "female"

            elif any(k in last_q for k in ["activity", "doing", "wyd", "up to", "plans", "hobbies"]):
                if any(re.search(p, low) for p in self.USER_NOTHING_PATTERNS) or low in ["nothing", "nm", "chilling", "bed", "music"]:
                    intents.add(UserIntent.USER_ANSWER_NOTHING)

        # 0. Stop and disconnect commands (Priority 1)
        for p in self.COMMAND_STOP_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.COMMAND_STOP)
                break

        # 1. Direct inquiries about the synthetic user
        for p in self.ASK_HOW_ARE_YOU_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.ASK_HOW_ARE_YOU)
                break

        for p in self.ASK_NAME_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.ASK_NAME)
                break

        for p in self.ASK_LOCATION_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.ASK_LOCATION)
                break

        for p in self.ASK_AGE_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.ASK_AGE)
                break

        for p in self.ASK_GENDER_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.ASK_GENDER)
                break

        for p in self.ASK_REASON_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.ASK_REASON)
                break

        for p in self.ASK_DOING_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.ASK_DOING)
                break

        # 2. Challenges and confusions
        for p in self.CHALLENGE_MAD_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.CHALLENGE_MAD)
                break

        for p in self.CHALLENGE_BOT_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.CHALLENGE_BOT)
                break

        for p in self.CONFUSION_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.CONFUSION)
                break

        # 3. Direct answers from user
        for p in self.USER_NO_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.USER_ANSWER_NO)
                break

        for p in self.USER_YES_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.USER_ANSWER_YES)
                break

        for p in self.USER_NOTHING_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.USER_ANSWER_NOTHING)
                break

        # 4. Greetings
        for p in self.GREETING_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.GREETING)
                break

        # 5. User Gender Statement
        # Match only if user is stating their own gender, not asking
        if not intents.intersection({UserIntent.ASK_GENDER}):
            if any(re.search(p, low) for p in self.GENDER_MALE_PATTERNS) and "female" not in low and "girl" not in low:
                intents.add(UserIntent.GENDER_MALE)
                entities["user_gender"] = "male"
            elif any(re.search(p, low) for p in self.GENDER_FEMALE_PATTERNS):
                intents.add(UserIntent.GENDER_FEMALE)
                entities["user_gender"] = "female"

        # 6. User Location Statement
        # Match only if not asking location
        if not intents.intersection({UserIntent.ASK_LOCATION}):
            for p in self.LOCATION_PATTERNS:
                m = re.search(p, low)
                if m:
                    intents.add(UserIntent.LOCATION)
                    loc_cand = m.group(1) if m.lastindex == 1 else m.group(m.lastindex)
                    loc_cand = loc_cand.strip().title()
                    if loc_cand.lower() not in ["from", "living in", "in", "located in"]:
                        entities["user_location"] = loc_cand
                    break

        # 7. User Age Statement
        # Match only if not asking age
        if not intents.intersection({UserIntent.ASK_AGE}):
            for p in self.AGE_PATTERNS:
                m = re.search(p, low)
                if m:
                    try:
                        age_val = int(m.group(1))
                        if 16 <= age_val <= 60:
                            intents.add(UserIntent.AGE)
                            entities["user_age"] = age_val
                            break
                    except Exception:
                        pass

        # 8. User Bored
        for p in self.BORED_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.BORED)
                break

        # 9. User Looking for friends/chat
        for p in self.LOOKING_PATTERNS:
            if re.search(p, low):
                if "friend" in low:
                    intents.add(UserIntent.LOOKING_FOR_FRIENDS)
                else:
                    intents.add(UserIntent.LOOKING_FOR_CHAT)
                break

        # 10. Flirting
        for p in self.FLIRTING_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.FLIRTING)
                break

        # 11. Bye and Disinterest
        for p in self.BYE_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.BYE)
                intents.add(UserIntent.DISINTEREST)
                break

        for p in self.DISINTEREST_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.DISINTEREST)
                break

        for p in self.POSITIVE_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.POSITIVE)
                break

        for p in self.NEGATIVE_PATTERNS:
            if re.search(p, low):
                intents.add(UserIntent.NEGATIVE)
                break

        # 12. Short Reply / Long Reply
        if is_short:
            intents.add(UserIntent.SHORT_REPLY)
        elif is_long:
            intents.add(UserIntent.LONG_REPLY)

        if not intents:
            intents.add(UserIntent.UNKNOWN)

        return ClassifiedMessage(
            raw_text=text,
            intents=list(intents),
            extracted_entities=entities,
            is_question=is_question,
            is_short=is_short,
            is_long=is_long,
        )
