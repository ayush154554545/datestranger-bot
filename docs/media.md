# Media Processing & Cloudflare R2 Pipeline

## 1. Overview
Handles media uploads, MIME detection, image/video compression, thumbnail generation, and object storage in Cloudflare R2.

---

## 2. Media Lifecycle
1. User sends photo / video / audio / voice in anonymous chat.
2. Bot extracts Telegram `file_id` and forwards media to matched partner.
3. Asynchronous worker (`workers/media/`) downloads binary via Telegram API.
4. Worker detects MIME type and generates WebP image / compressed thumbnail.
5. Uploads object to Cloudflare R2 (`profiles/`, `images/`, `videos/`, `audio/`, `voice/`).
6. Saves metadata entry in PostgreSQL `media` table (`object_key`, `checksum`, `mime_type`, `size`).
