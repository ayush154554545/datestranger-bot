# Feature Matrix & Specifications — Date Stranger Bot

## 1. Feature Specifications

### 1.1 18+ Profile Gating & Onboarding
* **Purpose**: Restrict access to legal adults (18+).
* **Inputs**: Age (Number 18-80), Gender (`Male`, `Female`, `Other`), Country (Selectable flag list), Language, Interest tags.
* **Rules**: Any user attempting to input an age below 18 receives an immediate safety rejection and cannot complete signup.

### 1.2 Anonymous Chat Relay
* **Purpose**: Enable 1-on-1 private conversation between matched strangers without revealing Telegram usernames or IDs.
* **Supported Media**: Text messages, Photos, Videos, Voice Notes, Audio files, Stickers, Documents, Animations, and Video Notes.
* **Privacy**: Forwarded messages strip sender attributes.

### 1.3 Priority Queue Matching Engine
* **Priority Calculation**:
  * `Admin`: Priority 20
  * `Premium`: Priority 10
  * `Free`: Priority 0
* **Mutual Filtering**: Premium users can set gender (`Male`, `Female`, `Any`) and age range (`Min`-`Max`). Matches occur only when filters align in both directions.

### 1.4 Telegram Stars Premium Purchasing
* **Payment Provider**: Telegram Stars (`XTR`).
* **Plans**:
  * 1 Week — 100 Stars
  * 1 Month — 300 Stars
  * 1 Year — 1,000 Stars
* **Idempotency**: Every transaction validates the unique `charge_id` prior to modifying expiration dates.

### 1.5 Referral System
* **Rules**: 5 verified user invites = 1 Day Premium.
* **Tracking**: Invites recorded via start parameters (`/start ref_<user_id>`). Fraudulent self-referrals blocked via user ID validation.

### 1.6 Moderation & Discord Audit Logging
* **Reports**: Direct reporting during chat with predefined reason categories.
* **Discord Logging**: Asynchronous logging of media files, voice messages, chat transcripts, and system alerts to configured webhooks.
