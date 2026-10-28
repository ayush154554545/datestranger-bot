# DateWithStranger - Master Development Rules (1 - 30)

This document establishes the 30 highest-level mandatory project rules for DateWithStranger.

---

### Rule 1: Inspect Before Modifying
Always thoroughly inspect existing source code, configuration files, and documentation before attempting any modification or architectural refactoring.

### Rule 2: Never Blindly Rewrite the Existing Bot
Treat the existing implementation (`bot/bot.py`) as a functional reference. Refactoring must preserve existing features and user flows unless explicitly updated by design.

### Rule 3: Preserve Behavior Unless Intentionally Changed
Do not remove existing functionality, commands, or callback features unless an explicit architectural change has been documented and approved.

### Rule 4: Website and Bot Remain Separate
The website and bot are distinct sub-projects. Website code (`website/`) must not drive bot architecture or access database tables directly using privileged credentials.

### Rule 5: PostgreSQL is Persistent Source of Truth
Supabase PostgreSQL is the sole persistent database. All user accounts, profiles, payments, matches, referrals, and moderation events must be durably stored in PostgreSQL.

### Rule 6: Redis is Temporary/Cache/Queue Infrastructure
Redis is for high-speed temporary state, waiting queue candidate caching, distributed locks, rate-limiting, and worker queues. Never treat Redis as permanent storage.

### Rule 7: Cloudflare R2 is Object Storage
All binary media assets (photos, videos, voice notes, audio, documents, PFPs) must be stored in Cloudflare R2. PostgreSQL stores media metadata only.

### Rule 8: Discord is Archival/Integration Infrastructure, Not Primary Database
Discord functions exclusively as an audit log and archive sink. Discord must never serve as a primary database.

### Rule 9: Critical Business Operations Must Not Depend Synchronously on Discord
Discord webhooks must run asynchronously on background worker queues. Discord failures, rate limits, or network timeouts must never impact Telegram bot response latency or rollback database transactions.

### Rule 10: Payments Must Be Idempotent
Payment processing (Telegram Stars) must enforce strict idempotency using unique transaction IDs (`charge_id`) to prevent double processing or duplicate premium grants.

### Rule 11: Matching Must Be Race-Condition Resistant
The matching engine must use atomic operations, database locks (`SKIP LOCKED`), or Redis reservation locks to prevent double-matching, stale queue assignments, or simultaneous matching race conditions.

### Rule 12: Secrets Must Never Be Committed
Bot tokens, Supabase service role keys, database connection URIs, Redis passwords, R2 keys, Discord webhooks, and payment secrets must never be committed to Git history.

### Rule 13: Secrets Must Never Be Logged
Loggers and Discord dispatchers must scrub secrets, private authorization tokens, and credentials prior to output.

### Rule 14: Never Expose Private User Information Publicly
Private user messages, profiles, and Telegram IDs must never be exposed publicly via web APIs or SEO landing pages.

### Rule 15: Enforce 18+ Eligibility
DateWithStranger is strictly an **18+ adult service**. The backend must enforce age eligibility (`CHECK (age >= 18)`) and reject minor participation.

### Rule 16: Every Feature Requires Tests
No new feature will be merged without corresponding automated unit, integration, or database test coverage.

### Rule 17: Every Bug Fix Requires Regression Tests Where Practical
Bug fixes must include a reproduction test confirming the fix and preventing regression.

### Rule 18: Never Fabricate Test Results
Never invent test suites, mock results, or status reports. Report actual execution status precisely (`PASS`, `FAIL`, `BLOCKED`).

### Rule 19: Never Claim Load Capacity Without Load Testing
Do not claim performance benchmarks or load capacity (e.g. 1,000 concurrent users) without empirical load test execution logs.

### Rule 20: Update Documentation After Architecture Changes
When code, schemas, or dependencies change, all corresponding documentation in `docs/` must be updated concurrently.

### Rule 21: Do Not Introduce Unnecessary Microservices
Avoid premature microservices decomposition. Design a clean modular monolith first.

### Rule 22: Prefer a Modular Monolith Initially
Structure the project cleanly into `bot/`, `api/`, `workers/`, `database/`, and `website/` within a unified codebase.

### Rule 23: Keep Expensive Work Asynchronous
Media processing, image compression, thumbnail generation, Discord archival, and analytics aggregation must run asynchronously in background workers (`workers/`).

### Rule 24: Use Database Constraints Where Appropriate
Enforce domain invariants using PostgreSQL primary keys, foreign keys, unique constraints, and check constraints (`CHECK (age >= 18)`).

### Rule 25: Minimize Stored Personal Data
Collect and store only necessary data required for bot functionality, safety moderation, and payment verification.

### Rule 26: Follow Documented Retention Policies
Adhere to data retention policies (`docs/data-retention.md`). Purge temporary media objects from R2 after retention expiry.

### Rule 27: Never Silently Change Product Behavior
Any behavioral modification must be explicitly documented in PRDs and release notes.

### Rule 28: Never Delete Functionality Without Explicit Approval
No handler, feature, or callback logic may be deleted without documented architectural approval.

### Rule 29: Security Takes Priority Over Convenience
Security controls, age gating, idempotency, and key isolation must take precedence over developer shortcuts.

### Rule 30: Performance Decisions Must Be Measurable
Performance optimizations must be justified by empirical benchmarking and metric measurements.
