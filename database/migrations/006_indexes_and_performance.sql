-- ============================================================================
-- MIGRATION 006: High-Performance B-Tree & Partial Indexes
-- ============================================================================

-- 1. Users & Identity Indexes
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_users_last_seen ON users(last_seen_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_account_status ON users(account_status);

-- 2. Demographics & Preferences Indexes
CREATE INDEX IF NOT EXISTS idx_profiles_gender ON profiles(gender);
CREATE INDEX IF NOT EXISTS idx_profiles_country ON profiles(country);
CREATE INDEX IF NOT EXISTS idx_profiles_age ON profiles(age);
CREATE INDEX IF NOT EXISTS idx_profiles_demographics ON profiles(gender, age, country);

-- 3. Queue & Match Engine Indexes
CREATE INDEX IF NOT EXISTS idx_waiting_queue_priority_time ON waiting_queue(priority DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_matches_status ON matches(status);
CREATE INDEX IF NOT EXISTS idx_matches_created_at ON matches(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_match_participants_user_id ON match_participants(user_id);
CREATE INDEX IF NOT EXISTS idx_match_participants_match_id ON match_participants(match_id);

-- 4. Messaging Indexes
CREATE INDEX IF NOT EXISTS idx_chat_sessions_match_id ON chat_sessions(match_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_time ON chat_messages(chat_session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_sender ON chat_messages(sender_user_id);

-- 5. Safety, Blocks, Bans & Reports Indexes
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_reported_user ON reports(reported_user_id);
CREATE INDEX IF NOT EXISTS idx_blocks_blocker_blocked ON blocks(blocker_user_id, blocked_user_id);
CREATE INDEX IF NOT EXISTS idx_bans_user_expiry ON bans(user_id, expires_at);

-- 6. Monetization & Growth Indexes
CREATE INDEX IF NOT EXISTS idx_premium_user_status ON premium_subscriptions(user_id, status, expires_at DESC);
CREATE INDEX IF NOT EXISTS idx_payments_provider_tx ON payment_transactions(provider_transaction_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_user_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referred ON referrals(referred_user_id);
