# DateWithStranger — Source Audit Report (Phase 0)

## 1. Executive Summary

This document provides a comprehensive audit of the **DateWithStranger** codebase as of Phase 0. It details the runtime environment, database architecture, third-party integrations, deployment configurations, and all environment variables discovered within the repository.

---

## 2. Current Runtime Specification

* **Primary Language**: Python 3.10+
* **Primary Bot Framework**: `pyTelegramBotAPI` (telebot) >= 4.20.0
* **API/Web Framework**: `Flask` >= 3.0.3 (configured for lightweight web hooks/status endpoints)
* **Data Validation & Settings**: `pydantic` >= 2.0.0, `pydantic-settings` >= 2.0.0
* **HTTP Client**: `requests` >= 2.31.0
* **Package Manager**: `pip` (`requirements.txt`)
* **Entry Points**:
  * `bot/src/datestranger/main.py`: Restructured modular Python entrypoint.
  * `bot/bot.py`: Monolithic legacy bot implementation (170KB, telebot event handlers).
  * `database/migrations/legacy/migrate_mongo_to_supabase.py`: Migration CLI script.
  * `website/index.html`: Web landing page interface.
* **Worker Processes**: Currently executed synchronously or in thread pools within `bot.py` / `main.py`. Asynchronous background workers planned for `workers/`.

---

## 3. Current Persistence Architecture

1. **Supabase PostgreSQL (Primary Target)**:
   * 8 Migration scripts present in `database/migrations/`:
     * `001_initial_schema.sql` (Users, Profiles, Settings)
     * `002_matches_and_chats.sql` (Waiting Queue, Matches, Chat Messages)
     * `003_moderation_and_admin.sql` (Reports, Blocks, Bans, Admin Audit)
     * `004_monetization_and_referrals.sql` (Subscriptions, Transactions, Referrals)
     * `005_analytics_and_system.sql` (Daily Stats, Advertisements)
     * `006_indexes_and_performance.sql` (GIN/B-Tree Indexes)
     * `007_rls_policies.sql` (Row Level Security)
     * `008_functions_and_triggers.sql` (Automated timestamps & counters)
   * Repository layer defined in `bot/src/datestranger/infrastructure/database/repositories/`.

2. **MongoDB (Legacy Persistence - Migration Source Only)**:
   * Collections: `users`, `waiting`, `active_chats`, `premium`, `invites`, `payments`, `reports`, `blocks`, `bans`, `daily_stats`, `settings`.
   * Driver: `pymongo` 4.10.1 (`dnspython` 2.6.1).
   * Status: **LEGACY READ-ONLY MIGRATION SOURCE**.

3. **Redis (High-Speed State & Queueing)**:
   * Driver: `redis` >= 5.0.0.
   * Client module: `bot/src/datestranger/infrastructure/redis/client.py`.
   * State managed: Active session locks, queue state, fallback in-memory state when disabled/offline.

---

## 4. Current Integrations

1. **Telegram Bot API**:
   * Interaction via `pyTelegramBotAPI`.
   * Modes supported: Long polling (default for local dev) and Webhook mode.
2. **Discord Archive & Webhook Logging System**:
   * 11 Webhooks configured for category-isolated event logging:
     * `STATUS_WEBHOOK` (System boot, heartbeat, health checks)
     * `ALERTS_WEBHOOK` (Errors, exceptions, critical security alerts)
     * `CHAT_LOG_WEBHOOK` (General text message logs)
     * `MEDIA_LOG_WEBHOOK` (Media message logs)
     * `VOICE_LOG_WEBHOOK` (Voice notes logs)
     * `GIRL_WEBHOOK` / `BOY_WEBHOOK` / `OTHER_WEBHOOK` (Gender-filtered user activities)
     * `GIRL_MEDIA_WEBHOOK` / `BOY_MEDIA_WEBHOOK` / `OTHER_MEDIA_WEBHOOK` (Gender-filtered media logs)
3. **Cloudflare R2 Object Storage**:
   * Intended for user profile pictures and persistent media uploads.
   * Configured via S3-compatible credentials in settings.

---

## 5. Current Infrastructure & Deployment Artifacts

* **Docker**: `Dockerfile` in root directory.
* **Render**: `render.yaml` configuration.
* **Fly.io**: `fly.toml` configuration.
* **Nixpacks**: `nixpacks.toml` configuration.
* **Heroku/Procfile**: `Procfile` (`worker: python bot/bot.py`).

---

## 6. Discovered Environment Variables

| Variable | Used By | Required | Secret | Current Purpose |
| -------- | ------- | -------- | ------ | --------------- |
| `APP_ENV` | `settings.py` | Recommended | No | Runtime environment (`development`, `production`, `test`) |
| `DEBUG` | `settings.py` | Recommended | No | Enables debug logging (`true`/`false`) |
| `BOT_TOKEN` | `settings.py`, `bot.py` | **Yes** | **Yes** | Telegram Bot API token |
| `ADMIN_ID` | `settings.py`, `bot.py` | **Yes** | No | Telegram user ID of system superadmin |
| `BOT_NAME` | `settings.py` | Recommended | No | Display name of the Telegram bot |
| `BOT_USER` | `settings.py` | Recommended | No | Username handle of Telegram bot |
| `TELEGRAM_MODE` | `settings.py` | Recommended | No | Connection mode (`polling` or `webhook`) |
| `TELEGRAM_WEBHOOK_URL` | `bot.py` | Optional | No | External URL for Telegram webhook |
| `SUPABASE_URL` | `settings.py`, `client.py` | **Yes** | No | Base REST/GraphQL URL for Supabase project |
| `SUPABASE_SERVICE_ROLE_KEY` | `settings.py`, `client.py` | **Yes** | **Yes** | Service role key (bypasses RLS for admin operations) |
| `SUPABASE_ANON_KEY` | `settings.py` | Optional | **Yes** | Client anon key for public endpoints |
| `SUPABASE_DB_URL` | Migration scripts | Optional | **Yes** | Direct PostgreSQL connection string |
| `MONGO_URL` | Legacy migration | Legacy | **Yes** | Connection string for MongoDB Atlas |
| `DB_NAME` | Legacy migration | Legacy | No | Legacy MongoDB database name |
| `REDIS_HOST` | `settings.py` | Recommended | No | Hostname for Redis instance |
| `REDIS_PORT` | `settings.py` | Recommended | No | Port for Redis instance (default `6379`) |
| `REDIS_PASSWORD` | `settings.py` | Optional | **Yes** | Password for authenticated Redis |
| `REDIS_DB` | `settings.py` | Recommended | No | Redis database index |
| `REDIS_ENABLED` | `settings.py` | Recommended | No | Flag to toggle Redis vs in-memory fallback |
| `REDIS_URL` | Unified Redis | Recommended | **Yes** | Standard Redis connection URL (`redis://...`) |
| `R2_ACCOUNT_ID` | `settings.py` | Optional | No | Cloudflare Account ID for R2 |
| `R2_ACCESS_KEY_ID` | `settings.py` | Optional | **Yes** | Access key ID for Cloudflare R2 |
| `R2_SECRET_ACCESS_KEY` | `settings.py` | Optional | **Yes** | Secret access key for Cloudflare R2 |
| `R2_BUCKET_NAME` | `settings.py` | Optional | No | R2 bucket name for media storage |
| `STATUS_WEBHOOK` | `settings.py`, `discord` | Recommended | **Yes** | Discord webhook URL for system status logs |
| `ALERTS_WEBHOOK` | `settings.py`, `discord` | Recommended | **Yes** | Discord webhook URL for error alerts |
| `CHAT_LOG_WEBHOOK` | `settings.py`, `discord` | Optional | **Yes** | Discord webhook URL for text chat logs |
| `MEDIA_LOG_WEBHOOK` | `settings.py`, `discord` | Optional | **Yes** | Discord webhook URL for media logs |
| `VOICE_LOG_WEBHOOK` | `settings.py`, `discord` | Optional | **Yes** | Discord webhook URL for voice logs |
| `GIRL_WEBHOOK` | `settings.py`, `discord` | Optional | **Yes** | Discord webhook for female user registrations |
| `BOY_WEBHOOK` | `settings.py`, `discord` | Optional | **Yes** | Discord webhook for male user registrations |
| `OTHER_WEBHOOK` | `settings.py`, `discord` | Optional | **Yes** | Discord webhook for other gender registrations |
| `GIRL_MEDIA_WEBHOOK` | `settings.py`, `discord` | Optional | **Yes** | Discord webhook for female user media |
| `BOY_MEDIA_WEBHOOK` | `settings.py`, `discord` | Optional | **Yes** | Discord webhook for male user media |
| `OTHER_MEDIA_WEBHOOK` | `settings.py`, `discord` | Optional | **Yes** | Discord webhook for other user media |
| `FFMPEG_PATH` | Media processing | Optional | No | System path to `ffmpeg` binary |
| `FFPROBE_PATH` | Media processing | Optional | No | System path to `ffprobe` binary |
| `JWT_SECRET` | Auth/API | Planned | **Yes** | Secret key for JWT signing |
| `SESSION_SECRET` | Auth/API | Planned | **Yes** | Secret key for web sessions |
