# ADR 008: Asynchronous Worker Queue Architecture

## Context
High-overhead operations (media compression, Discord logging, broadcast notifications, analytics aggregation) must not block the low-latency Telegram event loop.

## Decision
Establish dedicated **Background Workers** (`workers/`) powered by Redis task queues (Celery / ARQ / RQ).

## Alternatives Considered
- In-process thread spawning: Threatens thread pool exhaustion and memory bloat under load.

## Consequences
- Independent horizontal scaling of worker containers based on queue backlog depth.

## Status
ACCEPTED
