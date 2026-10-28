# MongoDB to Supabase Migration Operational Guide

## 1. Migration Overview
The migration process converts legacy MongoDB collections (`users`, `waiting`, `active_chats`, `premium`, `invites`, `payments`, `reports`, `blocks`, `bans`, `daily_stats`, `settings`) into normalized Supabase PostgreSQL tables.

## 2. Execution Steps
1. **Pre-flight Check**: Verify database connections and apply all migrations:
   ```bash
   python database/migrations/legacy/validate_migration.py --check-schema
   ```
2. **Execute Migration**: Run the migration script in idempotent mode:
   ```bash
   python database/migrations/legacy/migrate_mongo_to_supabase.py
   ```
3. **Validation**: Verify record counts, unique constraints, and hash checks:
   ```bash
   python database/migrations/legacy/validate_migration.py --verify-data
   ```

## 3. Rollback & Fail-Safe Strategy
- MongoDB collections remain untouched during migration.
- In case of unexpected failure, fix transformation errors and re-run `migrate_mongo_to_supabase.py` safely (uses `ON CONFLICT DO UPDATE` upsert logic).
