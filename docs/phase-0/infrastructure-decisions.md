# DateWithStranger — Infrastructure Architecture & Decisions (Phase 0)

This document outlines the architectural role and status of each infrastructure component within the **DateWithStranger** system ecosystem.

---

## 1. Architecture Map & Status Breakdown

### Component: Supabase PostgreSQL
* **Status**: `PLANNED` (Target Source of Truth)
* **Architectural Role**: Primary persistent relational database. Stores normalized user records, profiles, matching sessions, message metadata, moderation logs, admin actions, payments, and system configurations. Enforces relational constraints (FKs), check constraints (18+ gate), and Row Level Security (RLS).
* **Rationale**: Replaces legacy MongoDB to guarantee data integrity, relational queries, transaction safety, and native connection pool support.

---

### Component: MongoDB Atlas
* **Status**: `LEGACY` (Read-only migration source)
* **Architectural Role**: Legacy database containing historical user profiles, waiting lists, active chats, premium subscriptions, and activity logs.
* **Rationale**: Preserved strictly for Phase 2 data extraction and normalization script (`migrate_mongo_to_supabase.py`). Will be decommissioned after Phase 2 validation.

---

### Component: Redis / Upstash Redis
* **Status**: `CURRENT` (In-memory fallback available; Redis connection module active)
* **Architectural Role**: High-speed ephemeral state engine, matchmaking queues, chat session locking, rate limiting, and BullMQ worker queue state.
* **Rationale**: Guarantees atomic operations for stranger matching to prevent race conditions (two users matched to the same partner simultaneously).

---

### Component: Telegram Bot API
* **Status**: `CURRENT`
* **Architectural Role**: Primary end-user interface. Delivers conversational chat flows, media routing, button interactions, and user account onboarding.
* **Rationale**: DateWithStranger is fundamentally a Telegram stranger chat platform.

---

### Component: Discord Logging System
* **Status**: `CURRENT`
* **Architectural Role**: Out-of-band operational event streaming, real-time error notification, category-isolated chat logging, and gender-segmented activity monitoring.
* **Rationale**: Provides real-time administrative visibility without requiring custom web logging UI.

---

### Component: Cloudflare R2 Object Storage
* **Status**: `PLANNED`
* **Architectural Role**: S3-compatible cloud object storage for profile pictures, voice messages, and media content.
* **Rationale**: Eliminates storage constraints on database and application servers with zero egress costs.

---

### Component: Background Worker Subsystem (`workers/`)
* **Status**: `PLANNED`
* **Architectural Role**: Asynchronous worker pool handling Discord notification dispatching, media processing/compression (`ffmpeg`), analytics aggregation, and scheduled data retention cleanup.
* **Rationale**: Offloads heavy I/O and media processing tasks from the primary Telegram bot event loop.

---

### Component: REST / Web API (`api/` & `website/`)
* **Status**: `PLANNED`
* **Architectural Role**: External REST API and landing website serving public marketing pages, user portal, and web admin tools.
* **Rationale**: Decouples web frontend from Telegram bot core while reusing Supabase database backend.
