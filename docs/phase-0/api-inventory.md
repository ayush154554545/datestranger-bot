# DateWithStranger — API Inventory (Phase 0)

This document audits all external and internal Application Programming Interfaces (APIs) required by or integrated into the **DateWithStranger** project.

---

## 1. Telegram Bot API (External)

* **API**: Telegram Bot API (`https://api.telegram.org/bot<token>/`)
* **Purpose**: Core messaging, user identity fetching, inline keyboard interaction, media transfer, and bot state management.
* **Used by**: `bot/bot.py`, `bot/src/datestranger/bot/`.
* **Endpoint**: `https://api.telegram.org/bot<token>/[getUpdates, sendMessage, sendPhoto, sendVoice, setWebhook, getMe]`
* **Authentication**: Bot Token in URL path (`bot<BOT_TOKEN>`).
* **Credential**: `BOT_TOKEN`
* **Rate limits**: 30 messages/second system-wide; 1 message/second per chat ID.
* **Free tier**: 100% free with unlimited API calls subject to rate limits.
* **Failure behavior**: Retry on HTTP 429/5xx with exponential backoff. Catch `telebot.apihelper.ApiTelegramException` to handle blocked bot users (`403 Forbidden`).
* **Required**: `Yes`

---

## 2. Supabase REST & GraphQL API (External / Internal Database)

* **API**: Supabase PostgREST & Realtime API (`https://<project-ref>.supabase.co/rest/v1/`)
* **Purpose**: Relational database operations for users, profiles, matches, chat sessions, subscriptions, reports, and analytics.
* **Used by**: `bot/src/datestranger/infrastructure/database/client.py` and repository classes.
* **Endpoint**: `https://<project-ref>.supabase.co/rest/v1/[users, profiles, matches, chat_sessions, reports, payments]`
* **Authentication**: Bearer Token / API Key header (`apikey: <SUPABASE_SERVICE_ROLE_KEY>`, `Authorization: Bearer <SUPABASE_SERVICE_ROLE_KEY>`).
* **Credential**: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`
* **Rate limits**: Dependent on Supabase plan (Free tier supports high throughput for standard query volume).
* **Free tier**: 500 MB database, 50,000 monthly active users.
* **Failure behavior**: Catch connection timeouts and HTTP errors; log via `logger.error()`; fallback to offline/cached state where feasible.
* **Required**: `Yes`

---

## 3. Cloudflare R2 S3-Compatible API (External Storage)

* **API**: Cloudflare R2 Storage API (`https://<account-id>.r2.cloudflarestorage.com/`)
* **Purpose**: Offloading persistent storage of profile pictures, voice notes, and media uploads.
* **Used by**: `bot/src/datestranger/infrastructure/storage/r2_client.py` (Planned).
* **Endpoint**: S3-compatible endpoints (`GetObject`, `PutObject`, `DeleteObject`).
* **Authentication**: AWS Signature Version 4 (`R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`).
* **Credential**: `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `CLOUDFLARE_ACCOUNT_ID`
* **Rate limits**: High concurrency, virtually unlimited.
* **Free tier**: 10 GB monthly storage, 1M write operations, 10M read operations, $0 egress fees.
* **Failure behavior**: Fallback to direct Telegram file IDs if R2 upload fails.
* **Required**: `Recommended`

---

## 4. Discord Webhook API (External Logging)

* **API**: Discord Webhook API (`https://discord.com/api/webhooks/<id>/<token>`)
* **Purpose**: Category-isolated event logging, error streaming, chat archiving, and moderation monitoring.
* **Used by**: Discord logger module in bot settings.
* **Endpoint**: `https://discord.com/api/webhooks/...`
* **Authentication**: Token embedded in Webhook URL.
* **Credential**: `STATUS_WEBHOOK`, `ALERTS_WEBHOOK`, `CHAT_LOG_WEBHOOK`, `MEDIA_LOG_WEBHOOK`, `VOICE_LOG_WEBHOOK`, `GIRL_WEBHOOK`, `BOY_WEBHOOK`, `OTHER_WEBHOOK`
* **Rate limits**: 30 requests per 2 seconds per webhook channel.
* **Free tier**: 100% free.
* **Failure behavior**: Fail silently or buffer in outbox; never crash main Telegram bot thread on Discord HTTP failure.
* **Required**: `Recommended`

---

## 5. MongoDB Atlas REST/Driver API (Legacy Database)

* **API**: MongoDB Wire Protocol (`mongodb+srv://...`)
* **Purpose**: One-time data extraction during Phase 2 migration from legacy MongoDB to Supabase.
* **Used by**: `database/migrations/legacy/migrate_mongo_to_supabase.py`.
* **Endpoint**: MongoDB Atlas Cluster URI.
* **Authentication**: Username and Password credentials in connection URI.
* **Credential**: `MONGO_URL`, `DB_NAME`
* **Rate limits**: Plan dependent.
* **Free tier**: MongoDB M0 Free Cluster.
* **Failure behavior**: Log migration failure for specific batch; allow retry without duplicate inserts using upsert logic.
* **Required**: `Legacy` (Migration only)
