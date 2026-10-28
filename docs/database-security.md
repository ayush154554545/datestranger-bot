# Database Security & RLS Policy Specification

## 1. Security Architecture
- **Trusted Server Backend**: The Telegram bot, background workers, and API communicate with Supabase using the trusted `SUPABASE_SERVICE_ROLE_KEY`.
- **Public Client Isolation**: Web frontend and mobile clients interact via FastAPI REST endpoints or limited Supabase client SDKs restricted by Row-Level Security (RLS).
- **Service Role Protection**: `SUPABASE_SERVICE_ROLE_KEY` bypasses RLS and is restricted strictly to backend environment variables.

---

## 2. Row Level Security (RLS) Matrix

| Table | RLS Status | Anon Access | Authenticated User Access | Service Role Access |
| :--- | :--- | :--- | :--- | :--- |
| `users` | Enabled | None | Read own record (`auth.uid() = id`) | Full Access |
| `profiles` | Enabled | None | Read own profile, update own profile | Full Access |
| `user_preferences` | Enabled | None | Read/update own preferences | Full Access |
| `matches` | Enabled | None | Read matches where user is a participant | Full Access |
| `chat_messages` | Enabled | None | Read/Insert messages in active participant matches | Full Access |
| `reports` | Enabled | None | Insert own report, no read | Full Access |
| `blocks` | Enabled | None | Read/Insert own blocks | Full Access |
| `premium_subscriptions` | Enabled | None | Read own subscription | Full Access |
| `payment_transactions` | Enabled | None | Read own transaction history | Full Access |
| `admin_actions` | Enabled | None | None | Full Access |

---

## 3. Secret Isolation Guidelines
1. `SUPABASE_SERVICE_ROLE_KEY` must never be output in HTTP response headers, logs, or client-side JavaScript.
2. Production database connections enforce TLS/SSL connection parameters (`sslmode=require`).
