-- ============================================================================
-- MIGRATION 007: Row-Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on all sensitive application tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE match_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE blocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE bans ENABLE ROW LEVEL SECURITY;
ALTER TABLE premium_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_actions ENABLE ROW LEVEL SECURITY;

-- Service Role Policy (Bypasses RLS for trusted backend server operations)
-- Note: Supabase service_role automatically bypasses RLS in Postgres.

-- Client RLS Policies (For future public website/mobile client auth context)

-- Users Table Policies
CREATE POLICY "Users can view own profile" 
ON users FOR SELECT 
USING (auth.uid() = id);

CREATE POLICY "Users can update own record" 
ON users FOR UPDATE 
USING (auth.uid() = id);

-- Profiles Table Policies
CREATE POLICY "Users can view own profile details" 
ON profiles FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile details" 
ON profiles FOR UPDATE 
USING (auth.uid() = user_id);

-- Matches & Participants Policies
CREATE POLICY "Users can view matches they participate in" 
ON matches FOR SELECT 
USING (
    EXISTS (
        SELECT 1 FROM match_participants mp 
        WHERE mp.match_id = id AND mp.user_id = auth.uid()
    )
);

-- Chat Messages Policies
CREATE POLICY "Users can view messages in their active matches" 
ON chat_messages FOR SELECT 
USING (
    EXISTS (
        SELECT 1 FROM match_participants mp 
        JOIN chat_sessions cs ON cs.match_id = mp.match_id
        WHERE cs.id = chat_session_id AND mp.user_id = auth.uid()
    )
);

CREATE POLICY "Users can insert messages into their active matches" 
ON chat_messages FOR INSERT 
WITH CHECK (
    sender_user_id = auth.uid() AND
    EXISTS (
        SELECT 1 FROM match_participants mp 
        JOIN chat_sessions cs ON cs.match_id = mp.match_id
        WHERE cs.id = chat_session_id AND mp.user_id = auth.uid() AND mp.status = 'active'
    )
);

-- Reports Policies
CREATE POLICY "Users can submit reports" 
ON reports FOR INSERT 
WITH CHECK (reporter_user_id = auth.uid());

-- Blocks Policies
CREATE POLICY "Users can manage own blocks" 
ON blocks FOR ALL 
USING (blocker_user_id = auth.uid());

-- Payments & Subscriptions Policies
CREATE POLICY "Users can view own transactions" 
ON payment_transactions FOR SELECT 
USING (user_id = auth.uid());

CREATE POLICY "Users can view own premium status" 
ON premium_subscriptions FOR SELECT 
USING (user_id = auth.uid());
