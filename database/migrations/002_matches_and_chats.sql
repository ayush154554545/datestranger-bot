-- ============================================================================
-- MIGRATION 002: Matches, Queue, Participants, Chat Sessions, Messages & Media
-- ============================================================================

CREATE TYPE match_status_type AS ENUM ('active', 'ended', 'cancelled');
CREATE TYPE match_participant_status AS ENUM ('active', 'left', 'disconnected');
CREATE TYPE message_type_enum AS ENUM ('TEXT', 'PHOTO', 'VIDEO', 'AUDIO', 'VOICE', 'DOCUMENT', 'STICKER', 'VIDEO_NOTE', 'OTHER');

-- 1. Waiting Queue Table
CREATE TABLE IF NOT EXISTS waiting_queue (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    gender gender_type NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 18),
    country TEXT DEFAULT 'any',
    language TEXT DEFAULT 'en',
    preferred_gender gender_preference_type DEFAULT 'any',
    min_age INTEGER DEFAULT 18,
    max_age INTEGER DEFAULT 99,
    preferred_country TEXT DEFAULT 'any',
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Matches Table
CREATE TABLE IF NOT EXISTS matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status match_status_type DEFAULT 'active',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ NULL,
    ended_reason TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Match Participants Table
CREATE TABLE IF NOT EXISTS match_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status match_participant_status DEFAULT 'active',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ NULL,
    CONSTRAINT unique_match_participant UNIQUE (match_id, user_id)
);

-- CRITICAL CONCURRENCY CONTROL:
-- Partial Unique Index guaranteeing a user can ONLY belong to ONE active match at a time.
CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_match_per_user 
ON match_participants(user_id) 
WHERE (status = 'active');

-- 4. Chat Sessions Table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID UNIQUE NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Chat Messages Table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    sender_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipient_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_type message_type_enum DEFAULT 'TEXT',
    telegram_message_id BIGINT NULL,
    text_content TEXT NULL,
    media_id UUID NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
