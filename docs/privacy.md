# Privacy Policy & PII Protection Specification

## 1. Data Collection & Privacy Scope
DateWithStranger is an anonymous 18+ adult stranger dating platform.
- **Telegram User ID**: Stored as the primary system account identifier.
- **Profile Data**: Display name, age (18+ requirement), gender, country, and bio.
- **Location Data**: Country-level preference only; precise GPS coordinates are never collected or stored.
- **Chat Logs**: Ephemeral 1-on-1 chat logs are stored strictly for moderation and safety purposes.

## 2. PII Protection & Data Sanitization
1. Telegram usernames and user IDs are never exposed to match partners during anonymous chat sessions.
2. Public APIs must never serialize `telegram_user_id` or service credentials in public response payloads.
