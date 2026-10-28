# ADR 004: Asynchronous Discord Webhook Archival Pipeline

## Context
The legacy bot sent Discord log webhooks inline, causing thread stalls and risks when Discord rate-limited or dropped connections.

## Decision
Isolate Discord logging into an **Asynchronous Worker Queue** (`workers/discord/`). Discord functions purely as an audit/log sink with exponential backoff retries and dead-letter queues.

## Alternatives Considered
- Synchronous inline webhook HTTP calls: Blocks Telegram message relay during network delays.
- Replacing Discord logging entirely: Violates requirement to preserve existing audit webhook functionality.

## Consequences
- Zero impact on Telegram user latency if Discord experiences outages.
- Retry queue guarantees event delivery.

## Status
ACCEPTED
