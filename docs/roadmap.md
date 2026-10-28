# Technical Roadmap — Date Stranger Bot

## 1. Roadmap Phases & Implementation Strategy

```text
Phase 0: Source Audit & Architecture (COMPLETED)
   ↓
Phase 1: Modular Project Restructuring
   ↓
Phase 2: Supabase PostgreSQL Schema Deployment
   ↓
Phase 3: Repository & Data Layer Implementation
   ↓
Phase 4: Core Application Services
   ↓
Phase 5: 18+ Signup & Profile Onboarding
   ↓
Phase 6: Atomic Matching Engine
   ↓
Phase 7: Chat & Media Relay
   ↓
Phase 8: Reports & Moderation
   ↓
Phase 9: Telegram Stars Payments Subsystem
   ↓
Phase 10: Referral Subsystem
   ↓
Phase 11: Asynchronous Discord Integrations
   ↓
Phase 12: Admin Dashboard & Broadcaster
   ↓
Phase 13: MongoDB to Supabase Data Migration
   ↓
Phase 14: Production Deployment & Verification
   ↓
Phase 15: Postponed Website Integration
```

---

## 2. Phase Detail Breakdown

* **Phase 0 (Completed)**: Source inspection, separation of `website/` and `bot/`, creation of `.agent`, `.agents`, `.gemini`, root `rules.md`, `memory.md`, and full documentation framework.
* **Phase 1**: Restructure `bot/src/datestranger/` layout and configure typed settings module.
* **Phase 2**: Apply Supabase DDL migrations with 18+ check constraints and indexes.
* **Phase 3**: Implement repository pattern classes using Supabase Python SDK.
* **Phase 4**: Implement domain entities and application services.
* **Phase 5**: Build Telebot signup handlers enforcing 18+ age gate.
* **Phase 6**: Build PostgreSQL atomic queue matching engine.
* **Phase 7**: Build media relay services (Text, Photo, Video, Voice, Audio, Video Note).
* **Phase 8**: Build user report submission flow.
* **Phase 9**: Build Telegram Stars invoice & pre-checkout payment handlers with idempotency checks.
* **Phase 10**: Build referral link tracking and automated reward calculation.
* **Phase 11**: Build asynchronous Discord webhook dispatcher.
* **Phase 12**: Build admin controls, user watch service, and broadcast worker.
* **Phase 13**: Run data migration script to convert legacy MongoDB records to Supabase.
* **Phase 14**: Deploy to production container environment with zero downtime.
* **Phase 15**: Optional website web app integration (postponed).
