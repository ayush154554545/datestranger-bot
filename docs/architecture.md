# Full Architecture Overview — DateWithStranger

## 1. Architectural Philosophy
DateWithStranger is designed as a **Modular Monolith** initially, structured for clean future microservice extraction. High-speed Telegram interactions rely on lightweight presentation handlers, high-speed Redis temporary state caching, Supabase PostgreSQL persistence, Cloudflare R2 object storage, and asynchronous background worker queues.

---

## 2. Expanded System Architecture Diagram

```text
                    TELEGRAM
                        │
                        ▼
                    BOT APP
                        │
                ┌───────┴────────┐
                │                │
                ▼                ▼
             Redis           PostgreSQL
          queue/cache        Supabase
                │
        ┌───────┼──────────┐
        │       │          │
        ▼       ▼          ▼
      Media   Discord   Notifications
      Worker  Worker       Worker
        │
        ▼
       R2

                    API
                     │
          ┌──────────┴──────────┐
          │                     │
       Website                Admin
       Next.js                Panel
```

### Explanation of System Connections & Arrows:
1. **`TELEGRAM` $\rightarrow$ `BOT APP`**: Telegram delivers incoming updates, commands, and callbacks to the Python Bot Application (`bot/`).
2. **`BOT APP` $\rightarrow$ `Redis`**: The Bot Application queries Redis for fast candidate matching, active session state, rate-limiting, and ephemeral locks (`Redlock`).
3. **`BOT APP` $\rightarrow$ `PostgreSQL`**: The Bot Application reads and writes persistent accounts, profiles, 18+ eligibility flags, matches, subscriptions, and payment receipts (`UNIQUE(charge_id)`).
4. **`Redis` $\rightarrow$ `Media Worker`**: The Bot pushes binary media upload tasks to Redis worker queues. `Media Worker` downloads, compresses (WebP/H.264), and generates thumbnails off-thread.
5. **`Media Worker` $\rightarrow$ `R2`**: Compressed media binaries are uploaded directly to Cloudflare R2 object storage.
6. **`Redis` $\rightarrow$ `Discord Worker`**: Event logs are pushed to Redis queues. `Discord Worker` dispatches webhooks asynchronously with backoff retries.
7. **`Redis` $\rightarrow$ `Notifications Worker`**: Broadcast notifications and scheduled messages are pushed to Redis queues for batch delivery.
8. **`API` $\rightarrow$ `Website` / `Admin Panel`**: FastAPI (`api/`) serves REST API endpoints (`/api/v1/...`) for Next.js web components (`website/`) and administrative controls.

---

## 3. Component Separation & Responsibilities

| Component | Technology | Primary Responsibility |
| :--- | :--- | :--- |
| **`bot/`** | Python 3.11, TeleBot / aiogram | Handles Telegram bot user interactions, matching commands, and message forwarding. |
| **`api/`** | FastAPI, Pydantic | REST API for web clients, admin panel, health probes, and media upload signing. |
| **`website/`** | Next.js, TypeScript | Marketing landing pages, SEO, FAQ, safety policies, Terms of Service. |
| **`workers/`** | Redis Queue, Celery/ARQ | Offloads media processing, Discord webhooks, broadcast notifications, and cleanup. |
| **`database/`** | Supabase PostgreSQL | Single persistent source of truth. Enforces 18+ age checks (`CHECK (age >= 18)`). |
| **`Redis`** | Redis 7+ | Ephemeral cache, candidate queues, rate limiting, and distributed locks. |
| **`R2`** | Cloudflare R2 | S3-compatible binary media storage with zero egress bandwidth costs. |
