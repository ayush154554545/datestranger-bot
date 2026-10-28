# DateWithStranger — Webhook Inventory (Phase 0)

This document audits all webhooks used by or configured within the **DateWithStranger** system.

---

## 1. Discord Status & Alert Webhook

* **Webhook**: `STATUS_WEBHOOK` / `ALERTS_WEBHOOK`
* **Purpose**: Streams system lifecycle events (bot boot, graceful shutdown, health checks) and critical exceptions/error tracebacks to administrative Discord channels.
* **Source**: DateWithStranger Bot Application (`bot/src/datestranger/infrastructure/logging/discord_logger.py` or legacy `bot/bot.py`).
* **Destination**: Discord Channel (`#bot-status` / `#bot-alerts`).
* **Authentication**: Webhook URL path token.
* **Secret**: Yes (`ALERTS_WEBHOOK`, `STATUS_WEBHOOK` in `.env`).
* **Retry behavior**: Synchronous HTTP POST with standard 3-retries on 429 Rate Limit response.
* **Current implementation**: Direct inline `requests.post()` calls from bot event handlers.
* **Phase 2 recommendation**: Decouple from main bot execution loop using an in-memory/Redis outbox queue to prevent Discord network latency or outages from blocking Telegram bot responses.

---

## 2. Discord Chat & Media Webhooks

* **Webhook**: `CHAT_LOG_WEBHOOK` / `MEDIA_LOG_WEBHOOK` / `VOICE_LOG_WEBHOOK`
* **Purpose**: Logs user-to-user text messages, media files (photos, videos, documents), and voice notes to dedicated Discord archive channels for audit and moderation review.
* **Source**: DateWithStranger Bot Application.
* **Destination**: Discord Channels (`#chat-logs`, `#media-logs`, `#voice-logs`).
* **Authentication**: Webhook URL path token.
* **Secret**: Yes (`CHAT_LOG_WEBHOOK`, `MEDIA_LOG_WEBHOOK`, `VOICE_LOG_WEBHOOK` in `.env`).
* **Retry behavior**: Synchronous HTTP POST.
* **Current implementation**: Direct inline `requests.post()` calls inside telebot message handlers.
* **Phase 2 recommendation**: Offload to `workers/discord_worker.py` via Redis BullMQ queue or PostgreSQL outbox table to avoid Telegram handler latency spikes.

---

## 3. Discord Gender-Filtered Activity & Media Webhooks

* **Webhook**: `GIRL_WEBHOOK`, `BOY_WEBHOOK`, `OTHER_WEBHOOK`, `GIRL_MEDIA_WEBHOOK`, `BOY_MEDIA_WEBHOOK`, `OTHER_MEDIA_WEBHOOK`
* **Purpose**: Categorizes user registration, profile updates, and media uploads by gender for segmented administrative analytics and moderation monitoring.
* **Source**: DateWithStranger Bot Application.
* **Destination**: Gender-specific Discord Channels (`#female-users`, `#male-users`, `#female-media`, `#male-media`, etc.).
* **Authentication**: Webhook URL path token.
* **Secret**: Yes (Configured in `.env`).
* **Retry behavior**: Synchronous HTTP POST.
* **Current implementation**: Conditional logic checking user profile gender before posting to respective webhook.
* **Phase 2 recommendation**: Maintain existing gender filter classification logic, moving transmission to background worker.

---

## 4. Telegram Bot Incoming Webhook (Optional Mode)

* **Webhook**: `TELEGRAM_WEBHOOK_URL` (`/webhook/telegram`)
* **Purpose**: Receives incoming update payloads from Telegram servers when running in Webhook mode instead of Long Polling.
* **Source**: Telegram API Servers (`api.telegram.org`).
* **Destination**: DateWithStranger HTTP Server (`Flask` / `FastAPI` / `Hono` endpoint).
* **Authentication**: Secret Token Header (`X-Telegram-Bot-Api-Secret-Token`).
* **Secret**: Yes (`TELEGRAM_WEBHOOK_SECRET` in `.env`).
* **Retry behavior**: Telegram automatically retries failing webhooks with exponential backoff for up to 24 hours.
* **Current implementation**: Long Polling default (`bot.infinity_polling()`), with optional Webhook support in `bot.py`.
* **Phase 2 recommendation**: Use Long Polling during local development; support production deployment via secure HTTPS Webhook endpoint with IP whitelisting & secret token verification.
