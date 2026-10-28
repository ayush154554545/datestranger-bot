# DateWithStranger - Project Memory

- **Architecture**: Modular monolith with `bot/`, `api/`, `workers/`, `database/`, `website/`.
- **Database**: PostgreSQL (Supabase) + Redis.
- **Storage**: Cloudflare R2.
- **Constraints**: 18+ adult service, payment idempotency, zero secrets logged.
