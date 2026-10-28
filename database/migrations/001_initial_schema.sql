-- ============================================================================
-- MIGRATION 001: Initial Schema (Users, Profiles, Preferences, Settings)
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enum Types
CREATE TYPE user_account_status AS ENUM ('active', 'suspended', 'deleted');
CREATE TYPE user_eligibility_status AS ENUM ('unverified', 'eligible', 'ineligible', 'suspended');
CREATE TYPE gender_type AS ENUM ('male', 'female', 'other');
CREATE TYPE gender_preference_type AS ENUM ('male', 'female', 'other', 'any');

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_user_id BIGINT UNIQUE NOT NULL,
    telegram_username TEXT NULL,
    first_name TEXT NULL,
    last_name TEXT NULL,
    language_code TEXT DEFAULT 'en',
    account_status user_account_status DEFAULT 'active',
    eligibility_status user_eligibility_status DEFAULT 'unverified',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL
);

-- 2. Profiles Table (Enforces 18+ adult eligibility requirement)
CREATE TABLE IF NOT EXISTS profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    display_name TEXT NOT NULL,
    bio TEXT NULL,
    age INTEGER NOT NULL CONSTRAINT check_adult_age CHECK (age >= 18),
    gender gender_type NOT NULL,
    country TEXT DEFAULT 'any',
    language TEXT DEFAULT 'en',
    profile_status TEXT DEFAULT 'complete' CHECK (profile_status IN ('incomplete', 'complete', 'hidden')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. User Preferences Table
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    preferred_gender gender_preference_type DEFAULT 'any',
    min_age INTEGER DEFAULT 18 CONSTRAINT check_min_age CHECK (min_age >= 18),
    max_age INTEGER DEFAULT 99 CONSTRAINT check_max_age CHECK (max_age >= min_age),
    preferred_country TEXT DEFAULT 'any',
    preferred_language TEXT DEFAULT 'any',
    matching_mode TEXT DEFAULT 'standard',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. User Settings Table
CREATE TABLE IF NOT EXISTS user_settings (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    privacy_level TEXT DEFAULT 'standard',
    chat_settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Profile Photos Table
CREATE TABLE IF NOT EXISTS profile_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    telegram_file_id TEXT NOT NULL,
    telegram_file_unique_id TEXT NULL,
    storage_provider TEXT DEFAULT 'telegram',
    storage_key TEXT NULL,
    mime_type TEXT DEFAULT 'image/jpeg',
    width INTEGER NULL,
    height INTEGER NULL,
    file_size INTEGER NULL,
    checksum TEXT NULL,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
