# Performance Architecture & Optimization Strategy

## 1. Hot Paths vs. Cold Paths

### 1.1 Hot Paths (Must respond in < 150ms)
- Telegram update receipt and message relay forwarding.
- Finding match candidate in Redis queue.
- Pre-checkout Telegram Stars invoice validation.

### 1.2 Cold / Offloaded Paths (Executed asynchronously)
- Media compression (WebP / H.264) and Cloudflare R2 upload.
- Discord audit log webhook execution with retries.
- Broadcast notifications and daily analytics aggregation.

---

## 2. Key Optimization Practices
1. **Redis Candidate Caching**: Active queue candidates buffered in Redis sets to eliminate table scans on PostgreSQL during peak load.
2. **PostgreSQL Indexing**: B-tree indexes on `(priority DESC, entered_at ASC)` and `(telegram_id)`.
3. **Database Connection Pooling**: Connection pooler (`Supavisor` or `PgBouncer`) maintains active connections.
