# Environment Variable Specification & Configuration

## 1. Overview
All system configuration must be loaded from environment variables into typed configuration objects (Pydantic / Dataclasses). Direct inline calls to `os.getenv()` are forbidden in application logic.

---

## 2. Environment Variables Reference

| Category | Variable Name | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| **Telegram** | `BOT_TOKEN` | **YES** | Telegram Bot Authentication Token | `7890123456:ABCdef...` |
| **Supabase** | `SUPABASE_URL` | **YES** | Supabase Project API URL | `https://xyz.supabase.co` |
| **Supabase** | `SUPABASE_SERVICE_ROLE_KEY` | **YES** | Backend Server API Key (Bypasses RLS) | `eyJh...` |
| **Legacy DB** | `MONGO_URL` | Optional | Legacy MongoDB Connection String (Phase 0/1) | `mongodb+srv://...` |
| **Legacy DB** | `DB_NAME` | Optional | Legacy Mongo Database Name | `datestranger` |
| **Admin** | `ADMIN_ID` | **YES** | Telegram User ID of Master Administrator | `123456789` |
| **Discord Webhooks** | `STATUS_WEBHOOK` | Optional | Bot Status & Startup Webhook | `https://discord.com/api/webhooks/...` |
| **Discord Webhooks** | `ALERTS_WEBHOOK` | Optional | Error & System Alerts Webhook | `https://discord.com/api/webhooks/...` |
| **Discord Webhooks** | `CHAT_LOG_WEBHOOK` | Optional | Flushed Chat Transcript Webhook | `https://discord.com/api/webhooks/...` |
| **Discord Webhooks** | `MEDIA_LOG_WEBHOOK` | Optional | Media (Photo/Video) Log Webhook | `https://discord.com/api/webhooks/...` |
| **Discord Webhooks** | `GIRL_WEBHOOK` | Optional | Female Join Event Webhook | `https://discord.com/api/webhooks/...` |
| **Discord Webhooks** | `BOY_WEBHOOK` | Optional | Male Join Event Webhook | `https://discord.com/api/webhooks/...` |
| **Discord Webhooks** | `OTHER_WEBHOOK` | Optional | Other Gender Join Event Webhook | `https://discord.com/api/webhooks/...` |

---

## 3. Security Guidelines
* **DO NOT** commit `.env` or real secrets to repository control.
* Keep `bot/.env.example` updated with mock placeholders.
