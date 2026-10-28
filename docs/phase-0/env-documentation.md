# DateWithStranger — Environment Variables Specification & Reference (Phase 0)

This document provides exact, parameter-by-parameter documentation for every environment variable used in the **DateWithStranger** system architecture.

---

## 1. Application Core Configuration

### `APP_ENV`
* **Required**: Recommended
* **Used by**: `bot/src/datestranger/config/settings.py`
* **Purpose**: Defines the execution environment mode (`development`, `production`, `test`).
* **Where to obtain**: System administrator.
* **Exact setup steps**: Set in `.env` file or hosting container configuration.
* **Required permissions**: N/A
* **Development value**: `development`
* **Production value**: `production`
* **Security notes**: Public configuration flag. Non-sensitive.

---

### `DEBUG`
* **Required**: Recommended
* **Used by**: `bot/src/datestranger/config/settings.py`
* **Purpose**: Enables verbose debug logging and stack trace output.
* **Where to obtain**: Developer preference.
* **Exact setup steps**: Set in `.env` file (`true` or `false`).
* **Required permissions**: N/A
* **Development value**: `true`
* **Production value**: `false`
* **Security notes**: Set to `false` in production to prevent sensitive internal stack trace leakage in logs.

---

### `LOG_LEVEL`
* **Required**: Optional
* **Used by**: `bot/src/datestranger/infrastructure/logging/logger.py`
* **Purpose**: Controls logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
* **Where to obtain**: Developer preference.
* **Exact setup steps**: Set in `.env` file.
* **Required permissions**: N/A
* **Development value**: `DEBUG`
* **Production value**: `INFO`
* **Security notes**: Non-sensitive.

---

## 2. Telegram Bot Configuration

### `BOT_TOKEN`
* **Required**: Yes
* **Used by**: `bot/bot.py`, `bot/src/datestranger/config/settings.py`
* **Purpose**: Authentication token for Telegram Bot API.
* **Where to obtain**: Telegram `@BotFather`.
* **Exact setup steps**:
  1. Open Telegram app and start chat with `@BotFather`.
  2. Send `/newbot` or select existing bot via `/mybots`.
  3. Copy HTTP API Token string (format `1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ`).
  4. Paste into `.env`.
* **Required permissions**: Full bot API management.
* **Development value**: Dedicated test bot token from `@BotFather`.
* **Production value**: Production bot token from `@BotFather`.
* **Security notes**: Highly sensitive secret. Grants complete control over bot user communications. Never commit to repository or expose in logs.

---

### `ADMIN_ID`
* **Required**: Yes
* **Used by**: `bot/bot.py`, `bot/src/datestranger/config/settings.py`
* **Purpose**: Telegram User ID of superadmin with permission to issue admin commands (`/admin`, `/broadcast`, `/ban`, `/unban`, `/stats`).
* **Where to obtain**: Telegram `@userinfobot` or `@raw_data_bot`.
* **Exact setup steps**: Send `/start` to `@userinfobot` on Telegram to receive your numerical User ID.
* **Required permissions**: Telegram User Account ID.
* **Development value**: Developer Telegram User ID (e.g. `8835644904`).
* **Production value**: Production Admin Telegram User ID.
* **Security notes**: Administrative access controller. Keep accurate.

---

### `BOT_NAME`
* **Required**: Recommended
* **Used by**: `bot/src/datestranger/config/settings.py`
* **Purpose**: Display name of the Telegram bot for logging and message headers.
* **Where to obtain**: Configured during `@BotFather` setup.
* **Exact setup steps**: Set in `.env`.
* **Development value**: `DateWithStranger (Dev)`
* **Production value**: `DateWithStranger`
* **Security notes**: Non-sensitive.

---

### `BOT_USER`
* **Required**: Recommended
* **Used by**: `bot/src/datestranger/config/settings.py`
* **Purpose**: Telegram bot `@username` handle.
* **Where to obtain**: Configured during `@BotFather` setup.
* **Exact setup steps**: Set in `.env`.
* **Development value**: `@testdate27_bot`
* **Production value**: `@DateWithStrangerBot`
* **Security notes**: Public bot handle. Non-sensitive.

---

### `TELEGRAM_MODE`
* **Required**: Recommended
* **Used by**: `bot/bot.py`
* **Purpose**: Connection mode (`polling` or `webhook`).
* **Where to obtain**: System design decision.
* **Development value**: `polling`
* **Production value**: `webhook`
* **Security notes**: Non-sensitive.

---

## 3. Supabase PostgreSQL Configuration

### `SUPABASE_URL`
* **Required**: Yes
* **Used by**: `bot/src/datestranger/infrastructure/database/client.py`
* **Purpose**: Base REST/GraphQL API URL of Supabase project.
* **Where to obtain**: Supabase Dashboard → Project Settings → API.
* **Exact setup steps**:
  1. Log into [supabase.com](https://supabase.com).
  2. Select your project.
  3. Navigate to Project Settings → API.
  4. Copy `Project URL`.
* **Required permissions**: Project member access.
* **Development value**: `https://<dev-project-ref>.supabase.co`
* **Production value**: `https://<prod-project-ref>.supabase.co`
* **Security notes**: Public project endpoint. Safe to reference in backend code.

---

### `SUPABASE_SERVICE_ROLE_KEY`
* **Required**: Yes
* **Used by**: `bot/src/datestranger/infrastructure/database/client.py`
* **Purpose**: Administrative JWT key that bypasses Row Level Security (RLS) policies for server-side repository operations.
* **Where to obtain**: Supabase Dashboard → Project Settings → API → Service Role Key (`secret`).
* **Exact setup steps**:
  1. Go to Supabase Dashboard → Project Settings → API.
  2. Reveal `service_role` key under Project API Keys.
  3. Copy and paste into `.env`.
* **Required permissions**: Full Database Bypass RLS Admin Access.
* **Development value**: Dev environment Service Role Key.
* **Production value**: Prod environment Service Role Key.
* **Security notes**: **CRITICAL SECRET**. Bypasses all security policies. NEVER expose to client/frontend code, NEVER commit to Git, NEVER output in logs.

---

### `SUPABASE_ANON_KEY`
* **Required**: Optional
* **Used by**: `bot/src/datestranger/config/settings.py`
* **Purpose**: Public anonymous API key for frontend web queries subject to Row Level Security policies.
* **Where to obtain**: Supabase Dashboard → Project Settings → API → anon key.
* **Development value**: Dev anon key.
* **Production value**: Prod anon key.
* **Security notes**: Public client key. Enforces Row Level Security (RLS).

---

### `SUPABASE_DB_URL`
* **Required**: Optional (Required for direct SQL migrations / Alembic / `psycopg2`)
* **Used by**: Migration scripts (`database/migrations/`).
* **Purpose**: Direct PostgreSQL TCP connection string (`postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres`).
* **Where to obtain**: Supabase Dashboard → Project Settings → Database → Connection String → URI.
* **Security notes**: Contains database password. Server-side only.

---

## 4. Legacy MongoDB Configuration

### `MONGO_URL`
* **Required**: Legacy (Read-only data migration phase)
* **Used by**: `database/migrations/legacy/migrate_mongo_to_supabase.py`
* **Purpose**: Connection string to legacy MongoDB Atlas database.
* **Where to obtain**: MongoDB Atlas Dashboard → Database → Connect → Connection String.
* **Security notes**: Contains legacy database password. Keep read-only permissions during migration.

---

### `DB_NAME`
* **Required**: Legacy
* **Used by**: Legacy migration scripts.
* **Purpose**: MongoDB database name (`datestranger`).
* **Security notes**: Non-sensitive.

---

## 5. Redis Configuration

### `REDIS_HOST` / `REDIS_PORT` / `REDIS_PASSWORD` / `REDIS_URL`
* **Required**: Recommended
* **Used by**: `bot/src/datestranger/infrastructure/redis/client.py`
* **Purpose**: High-speed queueing, active chat session locking, and rate limiting.
* **Where to obtain**: Redis Cloud / Upstash Dashboard or local Docker instance.
* **Exact setup steps**:
  * Local Docker: `docker run -d -p 6379:6379 redis:7-alpine`
  * Upstash: Create database → Copy Connection String / Host / Password.
* **Development value**: `localhost` / `6379` (Local Docker)
* **Production value**: `REDIS_URL=rediss://default:<password>@<host>:<port>`
* **Security notes**: Server-side credential.

---

## 6. Cloudflare R2 Storage Configuration

### `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` / `R2_BUCKET_NAME` / `CLOUDFLARE_ACCOUNT_ID`
* **Required**: Recommended
* **Used by**: Cloudflare R2 S3 storage client.
* **Where to obtain**: Cloudflare Dashboard → R2 → Manage R2 API Tokens.
* **Exact setup steps**:
  1. Log into Cloudflare Dashboard.
  2. Select R2 → Manage R2 API Tokens.
  3. Create Token with Admin Read/Write permissions on target bucket.
  4. Copy Access Key ID and Secret Access Key.
* **Security notes**: S3 Access secrets must remain strictly on backend server.

---

## 7. Discord Logging Webhooks

### `STATUS_WEBHOOK` ... `OTHER_MEDIA_WEBHOOK`
* **Required**: Recommended
* **Used by**: Discord event logger.
* **Where to obtain**: Discord Server Settings → Integrations → Webhooks → New Webhook.
* **Exact setup steps**:
  1. Open Discord server channel settings.
  2. Select Integrations → Webhooks.
  3. Create Webhook, copy Webhook URL.
  4. Assign to respective environment variable.
* **Security notes**: Webhook URLs allow posting directly to Discord channels. Protect URLs from unauthorized posting.
