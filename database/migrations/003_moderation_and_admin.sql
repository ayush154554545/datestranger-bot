-- ============================================================================
-- MIGRATION 003: Moderation, Reports, Blocks, Bans, Admin Users & Audit Logs
-- ============================================================================

CREATE TYPE report_status_enum AS ENUM ('pending', 'investigating', 'resolved', 'dismissed');
CREATE TYPE ban_type_enum AS ENUM ('temporary', 'permanent');
CREATE TYPE admin_role_enum AS ENUM ('SUPER_ADMIN', 'ADMIN', 'MODERATOR', 'SUPPORT', 'ANALYST');

-- 1. Reports Table
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reported_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    match_id UUID NULL REFERENCES matches(id) ON DELETE SET NULL,
    reason TEXT NOT NULL,
    description TEXT NULL,
    status report_status_enum DEFAULT 'pending',
    assigned_admin_id UUID NULL REFERENCES users(id),
    resolution TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ NULL
);

-- 2. Blocks Table (Pairwise block protection preventing match pairing)
CREATE TABLE IF NOT EXISTS blocks (
    blocker_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    blocked_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (blocker_user_id, blocked_user_id)
);

-- 3. Bans Table
CREATE TABLE IF NOT EXISTS bans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ban_type ban_type_enum DEFAULT 'permanent',
    reason TEXT NOT NULL,
    created_by_user_id UUID NULL REFERENCES users(id),
    starts_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Admin Users Table
CREATE TABLE IF NOT EXISTS admin_users (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    role admin_role_enum DEFAULT 'MODERATOR',
    permissions JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Moderation Audit Trail Table
CREATE TABLE IF NOT EXISTS moderation_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_user_id UUID NOT NULL REFERENCES users(id),
    target_user_id UUID NOT NULL REFERENCES users(id),
    action_type TEXT NOT NULL,
    reason TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Admin Actions Audit Log
CREATE TABLE IF NOT EXISTS admin_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_user_id UUID NOT NULL REFERENCES users(id),
    action_type TEXT NOT NULL,
    target_user_id UUID NULL REFERENCES users(id),
    target_match_id UUID NULL REFERENCES matches(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
