# DateWithStranger — Service Inventory (Phase 0)

This document classifies every external service, API, runtime, database, storage system, and dependency associated with the **DateWithStranger** system.

---

## 1. Service Classification Summary

* **REQUIRED**: Telegram Bot API, Supabase PostgreSQL, Redis (or Redis In-Memory Fallback).
* **RECOMMENDED**: Discord Webhook Logging System, Cloudflare R2 Storage.
* **OPTIONAL**: Cloudflare API Token Management, Sentry Monitoring, Resend/SMTP Email.
* **LEGACY**: MongoDB Atlas (Read-only data migration source).
* **NOT NEEDED**: Stripe / Third-party Payment Gateway (Unless Telegram Payments or custom subscription system is activated).

---

## 2. Detailed Service Inventories

### Service: Telegram Bot API
* **Classification**: `REQUIRED`
* **Purpose**: Primary user interface and communication layer for stranger chat interactions.
* **Why needed**: End users interact with DateWithStranger entirely through Telegram bot commands, inline keyboards, media transfers, and state transitions.
* **Used by**: `bot/bot.py`, `bot/src/datestranger/main.py`.
* **Required now**: Yes.
* **Required later**: Yes.
* **Free tier available**: Yes (100% free Telegram Bot API).
* **Authentication required**: Yes.
* **Credentials required**: `BOT_TOKEN`, `ADMIN_ID`.
* **Local alternative**: Telegram Bot API Test Server / Mock Bot API.
* **Production alternative**: Official Telegram Bot API server / Self-hosted Telegram Bot API server for high-volume local file hosting.
* **Risk/limitation**: Telegram API rate limits (max 30 messages/sec system-wide, 1 message/sec per user chat).

---

### Service: Supabase PostgreSQL
* **Classification**: `REQUIRED`
* **Purpose**: Primary relational database source of truth for users, profiles, matches, chat sessions, moderation, admin, subscriptions, and analytics.
* **Why needed**: Replaces legacy schema-less MongoDB with ACID-compliant, highly structured relational database with strict foreign keys, check constraints (18+ verification), and RLS policies.
* **Used by**: `bot/src/datestranger/infrastructure/database/`, `database/migrations/`.
* **Required now**: Yes.
* **Required later**: Yes.
* **Free tier available**: Yes (Supabase Free Tier: 500MB database, 50k monthly active users).
* **Authentication required**: Yes.
* **Credentials required**: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`, `SUPABASE_DB_URL`.
* **Local alternative**: Local PostgreSQL Docker container (`postgres:15-alpine`).
* **Production alternative**: Managed PostgreSQL (AWS RDS, GCP Cloud SQL, Supabase Pro).
* **Risk/limitation**: Free tier pauses after 1 week of inactivity (can be unpaused or avoided with active heartbeat ping).

---

### Service: Redis / Upstash Redis
* **Classification**: `REQUIRED`
* **Purpose**: High-speed queueing, active chat session locks, rate limiting, temporary state, and BullMQ worker queue background processing.
* **Why needed**: Fast atomic matching queue operations and preventing race conditions during peer-to-peer stranger matching.
* **Used by**: `bot/src/datestranger/infrastructure/redis/client.py`.
* **Required now**: Recommended (In-memory fallback available for initial dev).
* **Required later**: Yes (Essential for 1,000+ concurrent active users).
* **Free tier available**: Yes (Upstash Redis free tier: 10,000 requests/day; Redis Cloud free 30MB instance; local Docker Redis).
* **Authentication required**: Yes (when using cloud Redis).
* **Credentials required**: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `REDIS_URL`.
* **Local alternative**: Local Redis Docker container (`redis:7-alpine`).
* **Production alternative**: Redis Cloud, Upstash Serverless Redis, ElastiCache.
* **Risk/limitation**: Out-of-memory errors if state TTL is not enforced.

---

### Service: Discord Webhooks
* **Classification**: `RECOMMENDED`
* **Purpose**: Real-time operational logging, category-isolated chat logs, gender activity tracking, system status alerts, and moderation event streaming.
* **Why needed**: Preserves existing functionality allowing admins to monitor bot activity, error spikes, and safety/moderation logs via Discord channels.
* **Used by**: `bot/src/datestranger/config/settings.py`, `bot/bot.py`.
* **Required now**: Optional for dev, Recommended for prod.
* **Required later**: Recommended.
* **Free tier available**: Yes (Discord webhooks are 100% free).
* **Authentication required**: Webhook token in URL.
* **Credentials required**: `STATUS_WEBHOOK`, `ALERTS_WEBHOOK`, `CHAT_LOG_WEBHOOK`, `MEDIA_LOG_WEBHOOK`, `VOICE_LOG_WEBHOOK`, `GIRL_WEBHOOK`, `BOY_WEBHOOK`, `OTHER_WEBHOOK`, `GIRL_MEDIA_WEBHOOK`, `BOY_MEDIA_WEBHOOK`, `OTHER_MEDIA_WEBHOOK`.
* **Local alternative**: Console logger / Local mock webhook server.
* **Production alternative**: Outbox worker pattern streaming to Discord API to avoid rate-limiting main bot thread.
* **Risk/limitation**: Discord webhook rate limits (30 requests per 2 seconds per webhook). Outbox queue required for high message rates.

---

### Service: Cloudflare R2 / S3 Storage
* **Classification**: `RECOMMENDED`
* **Purpose**: Storage for profile photos, user uploaded media, processed voice notes, and media backups.
* **Why needed**: Offloads persistent media storage from Telegram servers and database.
* **Used by**: `bot/src/datestranger/config/settings.py`.
* **Required now**: Optional.
* **Required later**: Recommended.
* **Free tier available**: Yes (Cloudflare R2 free tier: 10GB storage/month, 10M read operations, 1M write operations). Zero egress fees.
* **Authentication required**: Yes.
* **Credentials required**: `CLOUDFLARE_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`.
* **Local alternative**: MinIO local container or local filesystem storage.
* **Production alternative**: AWS S3, Cloudflare R2, Supabase Storage.
* **Risk/limitation**: Key leak risk if public bucket policy misconfigured. Access key must remain server-side.

---

### Service: MongoDB Atlas (Legacy)
* **Classification**: `LEGACY`
* **Purpose**: One-time source database for migrating existing user records, waiting queue data, active chats, bans, and history to Supabase PostgreSQL.
* **Why needed**: Preserves historical data during transition to new relational schema.
* **Used by**: `database/migrations/legacy/migrate_mongo_to_supabase.py`.
* **Required now**: Read-only during migration phase.
* **Required later**: No (to be decommissioned after Phase 2 migration).
* **Free tier available**: Yes (MongoDB Atlas M0 free tier).
* **Authentication required**: Yes.
* **Credentials required**: `MONGO_URL`, `DB_NAME`.
* **Local alternative**: Local MongoDB Docker container.
* **Production alternative**: Supabase PostgreSQL (Target).
* **Risk/limitation**: Must never write new production data to MongoDB after migration.

---

### Service: Sentry Monitoring
* **Classification**: `OPTIONAL`
* **Purpose**: Application performance monitoring and crash reporting.
* **Why needed**: Real-time exception tracking across production bot processes and background workers.
* **Used by**: Planned logger/monitoring integration.
* **Required now**: No.
* **Required later**: Recommended for high scale.
* **Free tier available**: Yes (Sentry Developer plan: 5,000 errors/month).
* **Authentication required**: Yes.
* **Credentials required**: `SENTRY_DSN`.
* **Local alternative**: Local logging to file/stdout.
* **Production alternative**: Sentry, Datadog, Prometheus/Grafana.
* **Risk/limitation**: Overhead on network if unhandled exception loops occur.
