# Supabase PostgreSQL Integration Guide

## 1. Architecture Summary
The DateWithStranger application uses **Supabase PostgreSQL** as its single persistent source of truth.

```text
Telegram Bot / FastAPI Server
           │
           ▼
 Repository Infrastructure (bot/src/datestranger/infrastructure/database)
           │
           ▼
   Supabase PostgreSQL
```

## 2. Environment Configuration
Required environment variables:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## 3. Directory Structure
```text
database/
├── migrations/          # Version-controlled SQL DDL scripts
│   ├── 001_initial_schema.sql
│   ├── 002_matches_and_chats.sql
│   ├── 003_moderation_and_admin.sql
│   ├── 004_monetization_and_referrals.sql
│   ├── 005_analytics_and_system.sql
│   ├── 006_indexes_and_performance.sql
│   ├── 007_rls_policies.sql
│   └── 008_functions_and_triggers.sql
├── seeds/               # Safe development & testing seeds
│   ├── development.sql
│   └── test.sql
├── docs/                # Schema DDL documentation
│   ├── schema.md
│   ├── indexes.md
│   ├── security.md
│   └── mongo-to-postgres-mapping.md
└── legacy/              # Migration & verification tools
    ├── migrate_mongo_to_supabase.py
    └── validate_migration.py
```
