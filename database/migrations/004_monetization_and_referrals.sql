-- ============================================================================
-- MIGRATION 004: Monetization (Telegram Stars), Premium & Referrals
-- ============================================================================

CREATE TYPE payment_status_enum AS ENUM ('pending', 'completed', 'failed', 'refunded');

-- 1. Premium Plans Table
CREATE TABLE IF NOT EXISTS premium_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    duration_days INTEGER NOT NULL,
    price_stars INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Premium Subscriptions Table
CREATE TABLE IF NOT EXISTS premium_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID NULL REFERENCES premium_plans(id),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'expired', 'cancelled')),
    starts_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    grant_history JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Payment Transactions Table (Idempotent charge_id check)
CREATE TABLE IF NOT EXISTS payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider TEXT DEFAULT 'telegram_stars',
    provider_transaction_id TEXT UNIQUE NOT NULL,
    plan_id UUID NULL REFERENCES premium_plans(id),
    amount NUMERIC(10, 2) NOT NULL,
    currency TEXT DEFAULT 'XTR',
    status payment_status_enum DEFAULT 'completed',
    payload JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Referrals Table (Attribution tracking with anti double-referral)
CREATE TABLE IF NOT EXISTS referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    referred_user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Referral Rewards Table
CREATE TABLE IF NOT EXISTS referral_rewards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    cycles_claimed INTEGER DEFAULT 0,
    days_awarded INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Advertisements Table
CREATE TABLE IF NOT EXISTS advertisements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    media_url TEXT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    impression_count INTEGER DEFAULT 0,
    starts_at TIMESTAMPTZ DEFAULT NOW(),
    ends_at TIMESTAMPTZ NULL,
    created_by_user_id UUID NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
