# Security & Safety Policy — Date Stranger Bot

## 1. Safety Policy: Mandatory 18+ Service Gate
Date Stranger is strictly an **adults-only (18+) service**. 

### 1.1 Policy Rules
1. **Age Threshold**: The minimum allowed age is **18 years old**.
2. **Deprecation of Minor Matching**: The legacy configuration (`MIN_AGE = 13`) has been completely revoked. Minor matching or interest categorization is strictly prohibited.
3. **Database Constraints**: The PostgreSQL schema enforces age eligibility at the database level:
   ```sql
   CONSTRAINT check_adult_age CHECK (age >= 18 AND age <= 80)
   ```
4. **Validation Layer**: The application onboarding wizard rejects any numeric age payload below 18 and halts signup.

---

## 2. Supabase Credential Security

| Credential Name | Scope / Exposure | Allowed Usage Locations | Security Restrictions |
| :--- | :--- | :--- | :--- |
| `SUPABASE_URL` | Public / Server | Server configuration, `.env` | Safe to include in backend environment configs. |
| `SUPABASE_ANON_KEY` | Public / Client | Frontend web apps, client apps | Protected by Row Level Security (RLS) policies. |
| `SUPABASE_SERVICE_ROLE_KEY` | **CRITICAL SERVER-ONLY** | Backend bot server only | **NEVER** expose to Telegram users, Git, logs, webhooks, or client code. Bypasses RLS. |

---

## 3. Data Protection & Privacy Guidelines
1. **Anonymous Chat Forwarding**: Telegram message forwarding strips sender identity, chat IDs, and usernames.
2. **Webhook Sanitization**: Discord logs scrub sensitive payment secrets, admin tokens, and private authentication keys before dispatching embeds.
3. **Token Management**: Telegram Bot Token (`BOT_TOKEN`) must only be supplied via environment variables (`.env`).
