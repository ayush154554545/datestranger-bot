# Background Workers (`workers/`)

Asynchronous background workers handling off-thread processing:

## Worker Subsystems
- `workers/media/`: Image/video/audio compression, thumbnail generation, R2 uploads.
- `workers/discord/`: Asynchronous Discord archive logging with exponential backoff retries.
- `workers/notifications/`: User notifications and broadcast queues.
- `workers/analytics/`: Daily stats aggregation and logging.
- `workers/cleanup/`: Expired match cleanup, temporary queue purging, stale lock releases.
