# PostgreSQL Relational Schema Specification

## 1. Core Tables

### 1.1 `users`
Identity table storing Telegram credentials and account state.
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `telegram_user_id` BIGINT UNIQUE NOT NULL
- `telegram_username` TEXT NULL
- `first_name` TEXT NULL
- `last_name` TEXT NULL
- `language_code` TEXT DEFAULT 'en'
- `account_status` TEXT DEFAULT 'active' CHECK (account_status IN ('active', 'suspended', 'deleted'))
- `eligibility_status` TEXT DEFAULT 'unverified' CHECK (eligibility_status IN ('unverified', 'eligible', 'ineligible', 'suspended'))
- `metadata` JSONB DEFAULT '{}'
- `created_at` TIMESTAMPTZ DEFAULT NOW()
- `updated_at` TIMESTAMPTZ DEFAULT NOW()
- `last_seen_at` TIMESTAMPTZ DEFAULT NOW()

### 1.2 `profiles`
Demographic and dating profile details.
- `user_id` UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE
- `display_name` TEXT NOT NULL
- `bio` TEXT NULL
- `age` INTEGER NOT NULL CHECK (age >= 18)
- `gender` TEXT NOT NULL CHECK (gender IN ('male', 'female', 'other'))
- `country` TEXT DEFAULT 'any'
- `language` TEXT DEFAULT 'en'
- `profile_status` TEXT DEFAULT 'complete' CHECK (profile_status IN ('incomplete', 'complete', 'hidden'))
- `created_at` TIMESTAMPTZ DEFAULT NOW()
- `updated_at` TIMESTAMPTZ DEFAULT NOW()

### 1.3 `user_preferences`
Filter preferences for stranger matching.
- `user_id` UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE
- `preferred_gender` TEXT DEFAULT 'any' CHECK (preferred_gender IN ('male', 'female', 'other', 'any'))
- `min_age` INTEGER DEFAULT 18 CHECK (min_age >= 18)
- `max_age` INTEGER DEFAULT 99 CHECK (max_age >= min_age)
- `preferred_country` TEXT DEFAULT 'any'
- `preferred_language` TEXT DEFAULT 'any'
- `created_at` TIMESTAMPTZ DEFAULT NOW()
- `updated_at` TIMESTAMPTZ DEFAULT NOW()

### 1.4 `user_settings`
Application preferences.
- `user_id` UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE
- `notifications_enabled` BOOLEAN DEFAULT TRUE
- `privacy_level` TEXT DEFAULT 'standard'
- `chat_settings` JSONB DEFAULT '{}'
- `created_at` TIMESTAMPTZ DEFAULT NOW()
- `updated_at` TIMESTAMPTZ DEFAULT NOW()

### 1.5 `profile_photos`
Avatar metadata.
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `telegram_file_id` TEXT NOT NULL
- `telegram_file_unique_id` TEXT NULL
- `storage_provider` TEXT DEFAULT 'telegram'
- `storage_key` TEXT NULL
- `mime_type` TEXT DEFAULT 'image/jpeg'
- `width` INTEGER NULL
- `height` INTEGER NULL
- `file_size` INTEGER NULL
- `checksum` TEXT NULL
- `is_current` BOOLEAN DEFAULT TRUE
- `created_at` TIMESTAMPTZ DEFAULT NOW()

---

## 2. Match & Chat Engine

### 2.1 `matches`
Persistent match sessions.
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `status` TEXT DEFAULT 'active' CHECK (status IN ('active', 'ended', 'cancelled'))
- `started_at` TIMESTAMPTZ DEFAULT NOW()
- `ended_at` TIMESTAMPTZ NULL
- `ended_reason` TEXT NULL
- `created_at` TIMESTAMPTZ DEFAULT NOW()

### 2.2 `match_participants`
Junction table linking users to matches. Contains partial unique index enforcing 1 active match per user.
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `match_id` UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE
- `user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `status` TEXT DEFAULT 'active' CHECK (status IN ('active', 'left', 'disconnected'))
- `joined_at` TIMESTAMPTZ DEFAULT NOW()
- `left_at` TIMESTAMPTZ NULL
- UNIQUE(match_id, user_id)

### 2.3 `chat_sessions`
Metadata container for message tracking.
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `match_id` UUID UNIQUE NOT NULL REFERENCES matches(id) ON DELETE CASCADE
- `message_count` INTEGER DEFAULT 0
- `last_message_at` TIMESTAMPTZ DEFAULT NOW()
- `created_at` TIMESTAMPTZ DEFAULT NOW()

### 2.4 `chat_messages`
Scalable message metadata table.
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `chat_session_id` UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE
- `sender_user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `recipient_user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `message_type` TEXT NOT NULL CHECK (message_type IN ('TEXT', 'PHOTO', 'VIDEO', 'AUDIO', 'VOICE', 'DOCUMENT', 'STICKER', 'VIDEO_NOTE', 'OTHER'))
- `telegram_message_id` BIGINT NULL
- `text_content` TEXT NULL
- `media_id` UUID NULL
- `created_at` TIMESTAMPTZ DEFAULT NOW()

---

## 3. Moderation, Safety & Administration

### 3.1 `reports`
User incident complaints.
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `reporter_user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `reported_user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `match_id` UUID NULL REFERENCES matches(id) ON DELETE SET NULL
- `reason` TEXT NOT NULL
- `description` TEXT NULL
- `status` TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'investigating', 'resolved', 'dismissed'))
- `assigned_admin_id` UUID NULL REFERENCES users(id)
- `created_at` TIMESTAMPTZ DEFAULT NOW()
- `resolved_at` TIMESTAMPTZ NULL

### 3.2 `blocks`
Personal user block pairings.
- `blocker_user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `blocked_user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `created_at` TIMESTAMPTZ DEFAULT NOW()
- PRIMARY KEY (blocker_user_id, blocked_user_id)

### 3.3 `bans`
System bans.
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `ban_type` TEXT DEFAULT 'permanent' CHECK (ban_type IN ('temporary', 'permanent'))
- `reason` TEXT NOT NULL
- `created_by_user_id` UUID NULL REFERENCES users(id)
- `starts_at` TIMESTAMPTZ DEFAULT NOW()
- `expires_at` TIMESTAMPTZ NULL
- `created_at` TIMESTAMPTZ DEFAULT NOW()

### 3.4 `moderation_actions`
Audit trail of moderation decisions.
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `admin_user_id` UUID NOT NULL REFERENCES users(id)
- `target_user_id` UUID NOT NULL REFERENCES users(id)
- `action_type` TEXT NOT NULL
- `reason` TEXT NOT NULL
- `metadata` JSONB DEFAULT '{}'
- `created_at` TIMESTAMPTZ DEFAULT NOW()

---

## 4. Monetization & Growth

### 4.1 `premium_plans`
Subscription tier metadata.
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `code` TEXT UNIQUE NOT NULL
- `name` TEXT NOT NULL
- `duration_days` INTEGER NOT NULL
- `price_stars` INTEGER NOT NULL
- `is_active` BOOLEAN DEFAULT TRUE
- `created_at` TIMESTAMPTZ DEFAULT NOW()

### 4.2 `premium_subscriptions`
Active and historical premium grants.
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `plan_id` UUID NULL REFERENCES premium_plans(id)
- `status` TEXT DEFAULT 'active' CHECK (status IN ('active', 'expired', 'cancelled'))
- `starts_at` TIMESTAMPTZ DEFAULT NOW()
- `expires_at` TIMESTAMPTZ NOT NULL
- `grant_history` JSONB DEFAULT '[]'
- `created_at` TIMESTAMPTZ DEFAULT NOW()
- `updated_at` TIMESTAMPTZ DEFAULT NOW()

### 4.3 `payment_transactions`
Receipts for Telegram Stars payments.
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `provider` TEXT DEFAULT 'telegram_stars'
- `provider_transaction_id` TEXT UNIQUE NOT NULL
- `plan_id` UUID NULL REFERENCES premium_plans(id)
- `amount` NUMERIC(10, 2) NOT NULL
- `currency` TEXT DEFAULT 'XTR'
- `status` TEXT DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed', 'refunded'))
- `payload` JSONB DEFAULT '{}'
- `created_at` TIMESTAMPTZ DEFAULT NOW()

### 4.4 `referrals` & `referral_rewards`
Growth tracking.
- `referrals`: `id`, `referrer_user_id`, `referred_user_id` (UNIQUE), `created_at`
- `referral_rewards`: `id`, `user_id`, `cycles_claimed`, `days_awarded`, `created_at`

---

## 5. Media, Events & System Configuration

### 5.1 `media` & `media_events`
- `media`: `id`, `owner_user_id`, `storage_provider`, `storage_key`, `mime_type`, `file_size`, `checksum`, `processing_status`, `created_at`
- `media_events`: `id`, `media_id`, `event_type`, `status`, `error_message`, `created_at`

### 5.2 `system_settings`
- `key` TEXT PRIMARY KEY
- `value` JSONB NOT NULL
- `updated_at` TIMESTAMPTZ DEFAULT NOW()

### 5.3 `daily_statistics`
- `stat_date` DATE PRIMARY KEY
- `new_users` INTEGER DEFAULT 0
- `active_users` INTEGER DEFAULT 0
- `matches_count` INTEGER DEFAULT 0
- `premium_sales` INTEGER DEFAULT 0
- `updated_at` TIMESTAMPTZ DEFAULT NOW()
