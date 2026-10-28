# MongoDB to PostgreSQL Mapping Specification

## 1. Overview
This document specifies the precise transformation rules, schema mappings, type conversions, and constraint implementations for migrating data from MongoDB to PostgreSQL (Supabase).

---

## 2. Comprehensive Collection to Table Mapping

### 2.1 `users` (Mongo) → `users`, `profiles`, `user_preferences`, `user_settings`
| Mongo Field | PostgreSQL Table | PostgreSQL Column | Data Type | Constraints & Transformation Rules |
| :--- | :--- | :--- | :--- | :--- |
| `_id` | `users` | `id` | `UUID` | Auto-generated UUID (`gen_random_uuid()`) |
| `user_id` | `users` | `telegram_user_id` | `BIGINT` | `UNIQUE NOT NULL` |
| `username` | `users` | `telegram_username` | `TEXT` | Nullable |
| `name` | `profiles` | `display_name` | `TEXT` | `NOT NULL` |
| `gender` | `profiles` | `gender` | `TEXT` | Enum: `'male'`, `'female'`, `'other'` |
| `age` | `profiles` | `age` | `INTEGER` | `CHECK (age >= 18)` (legacy under-18 values flagged for review) |
| `country` | `profiles` | `country` | `TEXT` | Default `'any'` |
| `language` | `profiles` | `language` | `TEXT` | Default `'en'` |
| `bio` | `profiles` | `bio` | `TEXT` | Nullable |
| `photo_file_id` | `profile_photos` | `telegram_file_id` | `TEXT` | Stored in `profile_photos` table |
| `search_preferences.preferred_gender` | `user_preferences` | `preferred_gender` | `TEXT` | Default `'any'` |
| `search_preferences.preferred_age_min` | `user_preferences` | `min_age` | `INTEGER` | Default `18` |
| `search_preferences.preferred_age_max` | `user_preferences` | `max_age` | `INTEGER` | Default `99` |
| `search_preferences.preferred_country` | `user_preferences` | `preferred_country` | `TEXT` | Default `'any'` |
| `registered_at` | `users` | `created_at` | `TIMESTAMPTZ` | UTC timestamp |
| `last_active` | `users` | `last_seen_at` | `TIMESTAMPTZ` | UTC timestamp |
| `total_chats`, `total_messages`, `total_time` | `users` | `metadata` | `JSONB` | Extensible metadata counters |

---

### 2.2 `waiting` (Mongo) → `waiting_queue`
| Mongo Field | PostgreSQL Column | Data Type | Constraints |
| :--- | :--- | :--- | :--- |
| `user_id` | `user_id` | `BIGINT` | `PRIMARY KEY REFERENCES users(telegram_user_id) ON DELETE CASCADE` |
| `gender`, `age`, `country`, `language` | Derived from `profiles` | - | Joined dynamically or snapshotted |
| `preferred_gender`, `preferred_age_min`, `preferred_age_max`, `preferred_country` | `preferred_gender`, `min_age`, `max_age`, `preferred_country` | `TEXT`, `INT`, `INT`, `TEXT` | Filter preferences |
| `priority` | `priority` | `INTEGER` | `DEFAULT 0` (Premium users have priority 10+) |
| `timestamp` | `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` |

---

### 2.3 `active_chats` (Mongo) → `matches`, `match_participants`, `chat_sessions`
| Mongo Field | PostgreSQL Table | PostgreSQL Column | Data Type | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `_id` | `matches` | `id` | `UUID` | `PRIMARY KEY` |
| `user1`, `user2` | `match_participants` | `user_id` | `BIGINT` | Two rows per match, `FK -> users(telegram_user_id)` |
| `started_at` | `matches` | `started_at` | `TIMESTAMPTZ` | `NOT NULL` |
| `last_message_at` | `chat_sessions` | `last_message_at` | `TIMESTAMPTZ` | `NOT NULL` |
| `messages_count` | `chat_sessions` | `message_count` | `INTEGER` | `DEFAULT 0` |

---

### 2.4 `premium` (Mongo) → `premium_subscriptions`
| Mongo Field | PostgreSQL Column | Data Type | Constraints |
| :--- | :--- | :--- | :--- |
| `user_id` | `user_id` | `BIGINT` | `FK -> users(telegram_user_id) ON DELETE CASCADE` |
| `is_premium` | `status` | `TEXT` | `'active'` if `expires_at > NOW()` else `'expired'` |
| `expires_at` | `expires_at` | `TIMESTAMPTZ` | Expiry timestamp |
| `history` | `grant_history` | `JSONB` | Entitlement audit log |

---

### 2.5 `invites` (Mongo) → `referrals`, `referral_rewards`
| Mongo Field | PostgreSQL Table | PostgreSQL Column | Data Type | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | `referrals` | `referrer_user_id` | `BIGINT` | `FK -> users(telegram_user_id)` |
| `invited_users` (array) | `referrals` | `referred_user_id` | `BIGINT` | `UNIQUE NOT NULL` |
| `redeemed_cycles` | `referral_rewards` | `cycles_claimed` | `INTEGER` | `DEFAULT 0` |

---

### 2.6 `payments` (Mongo) → `payment_transactions`
| Mongo Field | PostgreSQL Column | Data Type | Constraints |
| :--- | :--- | :--- | :--- |
| `charge_id` | `provider_transaction_id` | `TEXT` | `UNIQUE NOT NULL` |
| `user_id` | `user_id` | `BIGINT` | `FK -> users(telegram_user_id)` |
| `amount` | `amount` | `NUMERIC` | `NOT NULL` |
| `currency` | `currency` | `TEXT` | `DEFAULT 'XTR'` |
| `payload` | `payload` | `JSONB` | Metadata payload |
| `status` | `status` | `TEXT` | `'completed'` |
| `created_at` | `created_at` | `TIMESTAMPTZ` | Timestamp |

---

### 2.7 `reports` (Mongo) → `reports`
| Mongo Field | PostgreSQL Column | Data Type | Constraints |
| :--- | :--- | :--- | :--- |
| `reporter_id` | `reporter_user_id` | `BIGINT` | `FK -> users(telegram_user_id)` |
| `reported_id` | `reported_user_id` | `BIGINT` | `FK -> users(telegram_user_id)` |
| `reason` | `reason` | `TEXT` | `NOT NULL` |
| `details` | `description` | `TEXT` | Nullable |
| `status` | `status` | `TEXT` | `'pending'`, `'resolved'`, `'dismissed'` |
| `timestamp` | `created_at` | `TIMESTAMPTZ` | Timestamp |

---

### 2.8 `blocks` (Mongo) → `blocks`
| Mongo Field | PostgreSQL Column | Data Type | Constraints |
| :--- | :--- | :--- | :--- |
| `blocker_id` | `blocker_user_id` | `BIGINT` | `FK -> users(telegram_user_id)` |
| `blocked_id` | `blocked_user_id` | `BIGINT` | `FK -> users(telegram_user_id)` |
| `created_at` | `created_at` | `TIMESTAMPTZ` | Timestamp |
| - | - | - | `PRIMARY KEY (blocker_user_id, blocked_user_id)` |

---

### 2.9 `bans` (Mongo) → `bans`
| Mongo Field | PostgreSQL Column | Data Type | Constraints |
| :--- | :--- | :--- | :--- |
| `user_id` | `user_id` | `BIGINT` | `FK -> users(telegram_user_id)` |
| `reason` | `reason` | `TEXT` | `NOT NULL` |
| `banned_by` | `created_by` | `BIGINT` | Admin Telegram ID |
| `banned_at` | `created_at` | `TIMESTAMPTZ` | Timestamp |
| `expires_at` | `expires_at` | `TIMESTAMPTZ` | Nullable (null = permanent) |

---

### 2.10 `advertisements` (Mongo) → `advertisements`
| Mongo Field | PostgreSQL Column | Data Type | Constraints |
| :--- | :--- | :--- | :--- |
| `ad_id` | `id` | `UUID` | Primary Key |
| `title` | `title` | `TEXT` | `NOT NULL` |
| `content` | `content` | `TEXT` | `NOT NULL` |
| `active` | `status` | `TEXT` | `'active'`, `'inactive'` |
| `views_count` | `impression_count` | `INTEGER` | `DEFAULT 0` |

---

### 2.11 `daily_stats` (Mongo) → `daily_statistics`
| Mongo Field | PostgreSQL Column | Data Type | Constraints |
| :--- | :--- | :--- | :--- |
| `date` | `stat_date` | `DATE` | `PRIMARY KEY` |
| `new_users` | `new_users` | `INTEGER` | `DEFAULT 0` |
| `total_chats` | `total_matches` | `INTEGER` | `DEFAULT 0` |
| `active_users` | `active_users` | `INTEGER` | `DEFAULT 0` |

---

### 2.12 `settings` (Mongo) → `system_settings`
| Mongo Field | PostgreSQL Column | Data Type | Constraints |
| :--- | :--- | :--- | :--- |
| `key` | `key` | `TEXT` | `PRIMARY KEY` |
| `value` | `value` | `JSONB` | Dynamic setting payload |
| `updated` | `updated_at` | `TIMESTAMPTZ` | Timestamp |
