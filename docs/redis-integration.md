# Redis Caching & Queue Integration Plan

## 1. Overview
Redis will complement Supabase PostgreSQL by handling high-velocity ephemeral states, real-time matching candidate queues, and rate-limiting counters.

## 2. Shared Responsibilities
```text
Supabase PostgreSQL → Permanent Source of Truth (Profiles, Payments, Matches, Reports)
Redis                → High-Speed Ephemeral State (Matching Queue, Active Sockets, Rate Limits)
```

## 3. Planned Redis Usage
1. **Queue Candidate Caching**: `ZSET` sorted sets storing active search queue candidates (`score = priority + timestamp`).
2. **Session Locks**: Redlock distributed locking for multi-container match reservations.
3. **Rate Limiting**: Sliding window token buckets enforcing anti-spam policies.
