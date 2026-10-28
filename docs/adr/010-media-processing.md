# ADR 010: Media Processing & Optimization Strategy

## Context
Photos, videos, and voice notes uploaded by users must be compressed and formatted efficiently for web and app consumption without losing key quality or causing storage bloat.

## Decision
- **Images**: Compress to WebP / JPEG using Pillow / FFmpeg. Generate 200x200 thumbnails.
- **Audio / Voice**: Retain Opus / AAC compressed containers.
- **Storage**: Store processed binaries in Cloudflare R2; save metadata in PostgreSQL `media` table.

## Alternatives Considered
- Direct raw binary passthrough: Uncompressed high-res images waste R2 storage and bandwidth.

## Consequences
- 60-80% reduction in storage footprint and faster media load times.

## Status
ACCEPTED
