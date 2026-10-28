# Discord Webhook Integration Specification

## 1. Webhook Catalog & Mapping

| Environment Variable | Target Event Type | Payload Content | Failure Policy |
| :--- | :--- | :--- | :--- |
| `STATUS_WEBHOOK` | Bot Startup / Shutdown | Bot initialization state, uptime notification. | Non-blocking (Log & ignore failure) |
| `ALERTS_WEBHOOK` | Errors / Exceptions | Stack trace, unhandled error alert. | Non-blocking (Log & ignore failure) |
| `GIRL_WEBHOOK` | Female User Join | User ID, Name, Age, Country, Profile Embed. | Non-blocking (Log & ignore failure) |
| `BOY_WEBHOOK` | Male User Join | User ID, Name, Age, Country, Profile Embed. | Non-blocking (Log & ignore failure) |
| `OTHER_WEBHOOK` | Other Gender Join | User ID, Name, Age, Country, Profile Embed. | Non-blocking (Log & ignore failure) |
| `CHAT_LOG_WEBHOOK` | Chat Transcript Flush | Formatted transcript of ended anonymous chats. | Non-blocking (Log & ignore failure) |
| `MEDIA_LOG_WEBHOOK` | Media Relay Event | Forwarded Photo / Video media binary/URL. | Non-blocking (Log & ignore failure) |
| `VOICE_LOG_WEBHOOK` | Voice Relay Event | Forwarded Voice note binary. | Non-blocking (Log & ignore failure) |

---

## 2. Resilience Invariants
1. **Asynchronous Execution**: Webhook requests execute on background threads (`Thread(target=_send).start()`).
2. **Zero Blast Radius**: Failures, HTTP 5xx errors, rate limits, or timeouts (5s threshold) from Discord MUST NEVER crash or delay Telegram bot event loops or rollback database transactions.
3. **Data Scrubbing**: Secrets (`BOT_TOKEN`, `SUPABASE_SERVICE_ROLE_KEY`, payment charge tokens) are scrubbed before payload construction.
