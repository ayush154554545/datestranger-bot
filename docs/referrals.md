# Referral Subsystem Specification

## 1. Overview
The referral subsystem rewards existing users for inviting new users to Date Stranger.

---

## 2. Referral Mechanics & Reward Terms
* **Referral Link Format**: `https://t.me/testdate27_bot?start=ref_<telegram_id>`
* **Reward Cycle Threshold**: **5 Successful Invites**
* **Reward Granted**: **1 Day Premium Subscription** per cycle
* **Automated Cycle Redemption**: Rewards are granted automatically when invite counters reach $5, 10, 15, \dots$

---

## 3. Fraud Prevention & Attribution Rules
1. **Self-Referral Guard**: Referred user ID cannot equal referrer user ID.
2. **Completion Requirement**: A referral is **only credited** after the referred user completes the full 18+ profile setup (`signup_complete = true`).
3. **Single Attribution**: Each new Telegram user can be referred at most once (`UNIQUE(referred_user_id)`).
4. **Existing User Guard**: Users who previously signed up before receiving a referral link are ineligible.

---

## 4. Relational Database Implementation
Referrals are stored in two normalized Supabase tables:

```sql
-- Tracks valid attributions
CREATE TABLE referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    referred_user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tracks cycle reward grants
CREATE TABLE referral_rewards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reward_cycle INTEGER NOT NULL,
    days_granted INTEGER NOT NULL DEFAULT 1,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_referrer_cycle UNIQUE (referrer_id, reward_cycle)
);
```
