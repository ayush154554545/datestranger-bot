# ADR 001: Supabase PostgreSQL as Primary Persistent Storage

## Context
The legacy application used MongoDB, which lacked relational constraints, foreign keys, and strict age check constraints.

## Decision
Adopt **Supabase PostgreSQL** as the single source of truth for persistent data (users, profiles, matches, subscriptions, payments, referrals, reports, media metadata).

## Alternatives Considered
- MongoDB (Legacy): Prone to data inconsistency, lacks native declarative check constraints for 18+ verification.
- MySQL: Less rich JSONB/array support and weaker Supabase platform integration.

## Consequences
- Guaranteed relational integrity via Primary/Foreign keys.
- Declarative `CHECK (age >= 18)` constraint enforced at database level.
- Idempotency enforced via `UNIQUE(charge_id)` and `UNIQUE(referred_user_id)`.

## Status
ACCEPTED
