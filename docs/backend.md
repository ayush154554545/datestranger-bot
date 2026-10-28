# Backend Specification — Date Stranger Bot

## 1. Overview
The backend application provides core services for Date Stranger, bridging Telegram UI events with persistence layers, payment validation, matching algorithms, and external integrations.

---

## 2. Core Service Components

### 2.1 `MatchingService`
* **Responsibilities**: Queue management, mutual filtering validation, partner selection, atomic match creation, and queue withdrawal.
* **Concurrency Model**: Employs PostgreSQL row-level locks (`SELECT ... FOR UPDATE SKIP LOCKED`) to eliminate double-matching race conditions without needing process-bound Python locks.

### 2.2 `PaymentService`
* **Responsibilities**: Pre-checkout invoice validation, Telegram Stars charge recording, idempotent subscription extension, purchase audit logging.
* **Invariants**: Payments are strictly idempotent. Processing an identical `charge_id` multiple times yields no additional premium duration.

### 2.3 `ReferralService`
* **Responsibilities**: Referral link generation, attribution logging upon successful 18+ profile completion, reward threshold calculation (5 invites -> +1 Day Premium).

### 2.4 `DiscordWebhookService`
* **Responsibilities**: Asynchronous forwarding of gender join events, media logs, voice logs, chat transcripts, and system alerts to Discord channels.
* **Resilience**: Non-blocking thread execution with fallback error handling; network timeouts never impact Telegram user experience.
