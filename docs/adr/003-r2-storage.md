# ADR 003: Cloudflare R2 for Binary Media Storage

## Context
User profile pictures and shared chat media (photos, videos, audio, voice notes) must be stored reliably without bloating the PostgreSQL database or incurring high egress bandwidth costs.

## Decision
Use **Cloudflare R2** S3-compatible object storage for binary media assets. Store metadata (URLs, object keys, checksums, sizes, MIME types) in PostgreSQL.

## Alternatives Considered
- AWS S3: High egress bandwidth charges.
- Storing binary blobs directly in PostgreSQL: Causes database bloat and severe query degradation.

## Consequences
- Zero egress bandwidth fees on Cloudflare R2.
- High-speed global CDN delivery for public landing page media.

## Status
ACCEPTED
