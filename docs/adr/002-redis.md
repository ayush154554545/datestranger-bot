# ADR 002: Redis for Temporary State, Candidate Queues, and Distributed Locking

## Context
Matching 1,000+ concurrent users with mutual gender and age filters requires sub-millisecond candidate lookup and race-condition-free reservations.

## Decision
Utilize **Redis** as a high-speed ephemeral cache, waiting queue buffer, rate-limiter, and distributed lock provider (`Redlock`).

## Alternatives Considered
- Direct PostgreSQL polling for every queue check: Introduces high DB CPU overhead during peak load.
- In-memory Python dictionaries: Fails under multi-instance horizontal scaling.

## Consequences
- Redis acts purely as a temporary cache and queue buffer; PostgreSQL remains the persistent source of truth.
- Atomic candidate reservation prevents double-matching.

## Status
ACCEPTED
