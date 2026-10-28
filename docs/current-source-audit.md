# DateWithStranger Source Code Audit

## 1. Executive Summary
This document provides a comprehensive audit of the legacy DateWithStranger Telegram bot source code (`bot/bot.py`). It catalogues all database operations, collection schemas, index definitions, query patterns, in-memory volatile states, and technical risks to guide the migration to Supabase (PostgreSQL).

---

## 2. Legacy MongoDB Collections Audit

### 2.1 `users`
- **Purpose**: Identity, profile details, preferences, counters, and status.
- **Indexes**: `user_id` (Unique).
- **Document Structure**:
  ```json
  {
    "user_id": 123456789,
    "username": "johndoe",
    "name": "John",
    "gender": "male",
    "age": 22,
    "country": "US",
    "language": "en",
    "registered_at": "ISODate",
    "last_active": "ISODate",
    "is_banned": false,
    "is_vip": false,
    "total_chats": 12,
    "total_messages": 340,
    "total_time": 4500,
    "matches_count": 12,
    "reports_count": 0,
    "bio": "Hello there!",
    "photo_file_id": "AgACAgI...",
    "search_preferences": {
      "preferred_gender": "female",
      "preferred_age_min": 18,
      "preferred_age_max": 30,
      "preferred_country": "any"
    }
  }
  ```
- **Operations**: `find_one`, `insert_one`, `update_one` (`$set`, `$inc`), `aggregate`.

### 2.2 `waiting`
- **Purpose**: Active queue of users waiting to be matched.
- **Indexes**: `user_id` (Unique), `(priority DESC, timestamp ASC)`.
- **Document Structure**:
  ```json
  {
    "user_id": 123456789,
    "gender": "male",
    "age": 22,
    "country": "US",
    "language": "en",
    "preferred_gender": "female",
    "preferred_age_min": 18,
    "preferred_age_max": 30,
    "preferred_country": "any",
    "priority": 10,
    "timestamp": "ISODate"
  }
  ```
- **Operations**: `find_one`, `update_one` (`upsert=True`), `delete_one`, `find`.

### 2.3 `active_chats`
- **Purpose**: Active 1-on-1 chat pairings.
- **Indexes**: `user1`, `user2`.
- **Document Structure**:
  ```json
  {
    "user1": 123456789,
    "user2": 987654321,
    "started_at": "ISODate",
    "last_message_at": "ISODate",
    "messages_count": 45
  }
  ```
- **Operations**: `find_one`, `insert_one`, `delete_one`, `update_one` (`$inc`, `$set`).

### 2.4 `premium`
- **Purpose**: Tracks premium entitlements and entitlement history.
- **Indexes**: `user_id` (Unique).
- **Document Structure**:
  ```json
  {
    "user_id": 123456789,
    "is_premium": true,
    "expires_at": "ISODate",
    "updated_at": "ISODate",
    "history": [
      {
        "type": "purchase",
        "granted_at": "ISODate",
        "days": 30,
        "expires_at": "ISODate"
      }
    ]
  }
  ```
- **Operations**: `find_one`, `update_one` (`$set`, `$push`), `delete_one`.

### 2.5 `invites`
- **Purpose**: Referral counter and cycle tracking.
- **Indexes**: `user_id` (Unique).
- **Document Structure**:
  ```json
  {
    "user_id": 123456789,
    "invite_count": 5,
    "redeemed_cycles": 1,
    "invited_users": [987654321, 555444333]
  }
  ```
- **Operations**: `find_one`, `update_one` (`$setOnInsert`, `$inc`, `$push`).

### 2.6 `payments`
- **Purpose**: Telegram Stars payment logs and idempotency check.
- **Indexes**: `charge_id` (Unique).
- **Document Structure**:
  ```json
  {
    "user_id": 123456789,
    "charge_id": "STARS_CHARGE_998811",
    "amount": 100,
    "currency": "XTR",
    "payload": "premium_30_days",
    "status": "completed",
    "created_at": "ISODate"
  }
  ```
- **Operations**: `find_one`, `insert_one`.

### 2.7 `reports`
- **Purpose**: User complaints against match partners.
- **Document Structure**:
  ```json
  {
    "reporter_id": 123456789,
    "reported_id": 987654321,
    "reason": "inappropriate_behavior",
    "details": "Sent offensive text",
    "timestamp": "ISODate",
    "status": "pending"
  }
  ```
- **Operations**: `insert_one`, `find`, `update_one`.

### 2.8 `blocks`
- **Purpose**: Personal user block list (prevent re-matching).
- **Document Structure**:
  ```json
  {
    "blocker_id": 123456789,
    "blocked_id": 987654321,
    "created_at": "ISODate"
  }
  ```
- **Operations**: `insert_one`, `find_one`, `find`, `delete_one`.

### 2.9 `bans`
- **Purpose**: System-wide ban records.
- **Document Structure**:
  ```json
  {
    "user_id": 123456789,
    "reason": "spam",
    "banned_by": 8835644904,
    "banned_at": "ISODate",
    "expires_at": null
  }
  ```
- **Operations**: `insert_one`, `find_one`, `delete_one`.

### 2.10 `advertisements`
- **Purpose**: Ad campaign broadcasting.
- **Document Structure**:
  ```json
  {
    "ad_id": "AD_101",
    "title": "Promo",
    "content": "Check out our partner",
    "media_url": null,
    "active": true,
    "views_count": 1500,
    "created_at": "ISODate"
  }
  ```
- **Operations**: `insert_one`, `find`, `update_one`.

### 2.11 `daily_stats`
- **Purpose**: Historical daily metrics.
- **Indexes**: `date` (Unique).
- **Document Structure**:
  ```json
  {
    "date": "2026-10-01",
    "new_users": 150,
    "total_chats": 430,
    "active_users": 620,
    "premium_sales": 12
  }
  ```
- **Operations**: `update_one` (`upsert=True`), `find`.

### 2.12 `settings`
- **Purpose**: Dynamic system configuration (MOTD, feature toggles).
- **Document Structure**:
  ```json
  {
    "key": "motd",
    "value": "Welcome to Date Stranger!",
    "updated": "ISODate"
  }
  ```
- **Operations**: `find_one`, `update_one`, `delete_one`.

---

## 3. Volatile In-Memory State Audit
1. `user_states`: In-memory dictionary tracking multi-step onboarding wizard state.
2. `admin_states`: Multi-step admin command prompt state.
3. `watching_state`: Admin spectator mode active connections.
4. `active_chats_tracker`: Fast in-memory lookup dictionary for active chats.
5. `log_buffer`: Queue buffering messages before sending to Discord webhooks.

---

## 4. Technical Debt & Risks
- **Age Policy Enforcement**: Legacy default allows minors under 18. PostgreSQL schema will enforce `CHECK (age >= 18)`.
- **Single-Process Mutex**: Match lock `match_lock = Lock()` fails when horizontally scaled. Supabase transactional queue and partial unique indexes will guarantee 1 active match per user across distributed nodes.
- **Lack of Relational FKs**: MongoDB document references are unconstrained, risking orphaned records. PostgreSQL schema will enforce strict `FOREIGN KEY` constraints with `ON DELETE CASCADE / SET NULL`.
