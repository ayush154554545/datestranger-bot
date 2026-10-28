-- 009: allow 'couchbase' as a media storage provider (Capella media docs).
-- Additive: existing rows ('telegram', 'r2', 's3') are unaffected.
ALTER TABLE IF EXISTS media
    DROP CONSTRAINT IF EXISTS media_storage_provider_check;
ALTER TABLE IF EXISTS media
    ADD CONSTRAINT media_storage_provider_check
    CHECK (storage_provider IN ('telegram', 'r2', 's3', 'couchbase'));
