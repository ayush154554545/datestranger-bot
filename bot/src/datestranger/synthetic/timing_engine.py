"""
Timing Engine.
Calculates realistic human texting delays based on delay profiles,
message lengths, typing actions, and double message intervals.
"""

import random
from typing import Optional, Tuple
from datestranger.synthetic.models import DelayProfile, SyntheticProfile


class TimingEngine:
    """
    Computes human-like response delays and typing intervals.
    """

    def __init__(self, rng: Optional[random.Random] = None, speed_multiplier: float = 1.0):
        self.rng = rng or random.Random()
        # speed_multiplier can be set lower (e.g. 0.05) during unit tests for instant simulation
        self.speed_multiplier = speed_multiplier

    def calculate_reply_delay(
        self,
        profile: SyntheticProfile,
        text_length: int,
        is_opening: bool = False
    ) -> float:
        """
        Calculates human thinking time + typing delay in seconds.
        """
        profile_type = profile.response_delay_profile

        if profile_type == DelayProfile.FAST:
            base_delay = self.rng.uniform(2.0, 7.5)
        elif profile_type == DelayProfile.NORMAL:
            base_delay = self.rng.uniform(7.0, 22.0)
        elif profile_type == DelayProfile.SLOW:
            base_delay = self.rng.uniform(18.0, 50.0)
        elif profile_type == DelayProfile.INCONSISTENT:
            # 40% fast, 40% normal, 20% slow
            roll = self.rng.random()
            if roll < 0.40:
                base_delay = self.rng.uniform(3.0, 8.0)
            elif roll < 0.80:
                base_delay = self.rng.uniform(10.0, 30.0)
            else:
                base_delay = self.rng.uniform(35.0, 65.0)
        else:
            base_delay = self.rng.uniform(5.0, 15.0)

        # Longer messages take slightly longer to type (proportional to character count)
        # Average typing speed: ~4-6 characters per second
        typing_time = max(1.0, min(8.0, (text_length / 25.0) * self.rng.uniform(1.0, 1.8)))

        # Opening messages are slightly faster (user just arrived or greeting was ready)
        if is_opening:
            total_delay = min(base_delay, 5.0) + self.rng.uniform(0.5, 1.5)
        else:
            total_delay = base_delay + typing_time

        return round(total_delay * self.speed_multiplier, 2)

    def calculate_double_message_gap(self) -> float:
        """Gap between first and second message in double-message turns."""
        return round(self.rng.uniform(1.5, 3.5) * self.speed_multiplier, 2)
