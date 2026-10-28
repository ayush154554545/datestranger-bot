-- ============================================================================
-- MIGRATION 005: Analytics, Notifications, Media, Outbox & System Settings
-- ============================================================================

-- 1. System Settings Table
CREATE TABLE IF NOT EXISTS system_settings (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Daily Statistics Table
CREATE TABLE IF NOT EXISTS daily_statistics (
    stat_date DATE PRIMARY KEY,
    new_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    matches_count INTEGER DEFAULT 0,
    messages_count INTEGER DEFAULT 0,
    reports_count INTEGER DEFAULT 0,
    premium_sales INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    payload JSONB DEFAULT '{}'::jsonb,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
    scheduled_at TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Media Metadata Table (Cloudflare R2 Object Storage ready)
CREATE TABLE IF NOT EXISTS media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_id UUID NULL REFERENCES chat_messages(id) ON DELETE SET NULL,
    storage_provider TEXT DEFAULT 'telegram' CHECK (storage_provider IN ('telegram', 'r2', 's3')),
    storage_key TEXT NULL,
    original_filename TEXT NULL,
    mime_type TEXT DEFAULT 'application/octet-stream',
    file_size INTEGER NULL,
    checksum TEXT NULL,
    width INTEGER NULL,
    height INTEGER NULL,
    duration INTEGER NULL,
    processing_status TEXT DEFAULT 'ready' CHECK (processing_status IN ('pending', 'processing', 'ready', 'failed', 'deleted')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Media Events Processing Table
CREATE TABLE IF NOT EXISTS media_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_id UUID NOT NULL REFERENCES media(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    error_message TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Discord Outbox Audit Events Table
CREATE TABLE IF NOT EXISTS discord_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    discord_channel_id TEXT NULL,
    payload JSONB DEFAULT '{}'::jsonb,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
    attempts INTEGER DEFAULT 0,
    last_error TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ NULL
);

-- 7. Outbox Events Pattern Table for Async Processing
CREATE TABLE IF NOT EXISTS outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    aggregate_type TEXT NOT NULL,
    aggregate_id UUID NOT NULL,
    payload JSONB DEFAULT '{}'::jsonb,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processed', 'failed')),
    attempts INTEGER DEFAULT 0,
    available_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
