# Product Requirements Document (PRD) — Date Stranger Bot

## 1. Executive Summary & Purpose
**Date Stranger** is an anonymous 1-on-1 dating and stranger chat Telegram bot. It connects users based on mutual gender, age, country, and interest preferences while providing premium priority matching, safety reporting, referral rewards, and automated Discord audit logging.

---

## 2. Safety & Eligibility (18+ Mandatory)
* **Age Requirement**: All users MUST be **18 years of age or older**.
* **Age Gate Enforcement**: The system prompts for age during profile setup and rejects any input below 18 (`CHECK (age >= 18)`).
* **Minor Protection**: Sexual, intimate, or dating matching for minors is strictly prohibited and removed from system scope.

---

## 3. Core Feature Specifications

### 3.1 Signup & Profile Management
* **Status**: `CURRENT` (refactoring to relational DB planned)
* **Flow**:
  1. User issues `/start`.
  2. Age confirmation (Must be 18-80).
  3. Gender selection (`Male`, `Female`, `Other`).
  4. Country selection.
  5. Language selection.
  6. Interest tag selection (`Chatting`, `Flirting`, `Bored`, `Love`, `Relationship`, `Intimacy`).
* **Requirements**: Profile updates accessible via `/settings`.

### 3.2 Anonymous Matching Engine
* **Status**: `CURRENT` (refactoring to PostgreSQL atomic matching planned)
* **Flow**:
  1. User taps "🔍 Find Match".
  2. User is added to `waiting_queue` with priority score (`Admin` = 20, `Premium` = 10, `Free` = 0).
  3. Engine scans queue for compatible partner satisfying mutual gender and age filters.
  4. Upon match, both users receive notification with partner alias, age, gender emoji, and country.
* **Requirements**: Double-matching and self-matching strictly prevented.

### 3.3 Active Anonymous Chat Relay
* **Status**: `CURRENT`
* **Features**:
  * Bidirectional relay of text, photos, videos, voice notes, stickers, documents, animations, and video notes.
  * Partner leave (`/leave` or "🚪 Leave Chat").
  * Next partner (`/next` or "➡️ Next Stranger").
  * Report partner (`/report` or "🚨 Report").

### 3.4 Premium Subsystem (Telegram Stars)
* **Status**: `CURRENT`
* **Plans**:
  * 1 Week: 100 Stars
  * 1 Month: 300 Stars
  * 1 Year: 1,000 Stars
* **Perks**:
  * Priority queue placement (`priority = 10`).
  * Active gender filtering (`Filter by Male/Female/Any`).
  * Active age range filtering (`Filter by Min/Max Age`).
  * Special profile badge (`⭐ Premium`).

### 3.5 Referral Subsystem
* **Status**: `CURRENT`
* **Incentive**: 5 valid user invites = 1 Day Premium reward.
* **Fraud Prevention**: Rejects self-referral, duplicate account claims, and un-completed profiles.

### 3.6 Moderation, Reports & Admin System
* **Status**: `CURRENT`
* **Features**:
  * User reporting with reason categories (`Nudity/NSFW`, `Spam/Scam`, `Abuse/Harassment`, `Underage`, `Other`).
  * Real-time admin user watching (`/watch <user_id>`).
  * User banning (`/ban <user_id> <reason>`).
  * Global broadcast command (`/broadcast`).
  * Live statistics dashboard (`/stats`).

---

## 4. System Classification Matrix

| Feature | Classification | Description |
| :--- | :--- | :--- |
| Anonymous 1-on-1 Chat | `CURRENT` | Core stranger relay functionality. |
| 18+ Age Verification | `CURRENT` | Backend age validation. |
| Telegram Stars Payments | `CURRENT` | In-app digital product purchase. |
| Supabase Relational Migration | `PLANNED` | PostgreSQL schema migration from MongoDB. |
| Modular Clean Architecture | `PLANNED` | Separating `bot.py` into application layers. |
| Minor Sexual Categories | `DEPRECATED` | Removed from product scope. |
| Embedded Web App UI | `FUTURE` | Postponed in `website/`. |
