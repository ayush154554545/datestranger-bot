-- ============================================================================
-- MIGRATION 008: Database Functions & Triggers
-- ============================================================================

-- 1. Automatic Timestamp Trigger Function
CREATE OR REPLACE FUNCTION update_timestamp_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply timestamp trigger to core tables
DROP TRIGGER IF EXISTS trigger_update_users_timestamp ON users;
CREATE TRIGGER trigger_update_users_timestamp
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

DROP TRIGGER IF EXISTS trigger_update_profiles_timestamp ON profiles;
CREATE TRIGGER trigger_update_profiles_timestamp
BEFORE UPDATE ON profiles
FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

DROP TRIGGER IF EXISTS trigger_update_user_preferences_timestamp ON user_preferences;
CREATE TRIGGER trigger_update_user_preferences_timestamp
BEFORE UPDATE ON user_preferences
FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

-- 2. Atomic Transaction Function for Match Creation
CREATE OR REPLACE FUNCTION create_atomic_match(
    p_user1_id UUID,
    p_user2_id UUID
)
RETURNS TABLE (
    out_match_id UUID,
    out_chat_session_id UUID
) AS $$
DECLARE
    v_match_id UUID;
    v_chat_session_id UUID;
BEGIN
    -- Verify neither user is already in an active match
    IF EXISTS (
        SELECT 1 FROM match_participants 
        WHERE user_id IN (p_user1_id, p_user2_id) AND status = 'active'
    ) THEN
        RAISE EXCEPTION 'One or both users are already in an active match.';
    END IF;

    -- Create match entity
    INSERT INTO matches (status, started_at)
    VALUES ('active', NOW())
    RETURNING id INTO v_match_id;

    -- Insert participant 1
    INSERT INTO match_participants (match_id, user_id, status, joined_at)
    VALUES (v_match_id, p_user1_id, 'active', NOW());

    -- Insert participant 2
    INSERT INTO match_participants (match_id, user_id, status, joined_at)
    VALUES (v_match_id, p_user2_id, 'active', NOW());

    -- Create corresponding chat session
    INSERT INTO chat_sessions (match_id, message_count, last_message_at)
    VALUES (v_match_id, 0, NOW())
    RETURNING id INTO v_chat_session_id;

    -- Remove both users from the waiting queue
    DELETE FROM waiting_queue WHERE user_id IN (p_user1_id, p_user2_id);

    out_match_id := v_match_id;
    out_chat_session_id := v_chat_session_id;
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- 3. Idempotent Function for Granting Premium Subscriptions
CREATE OR REPLACE FUNCTION grant_premium_subscription(
    p_user_id UUID,
    p_days INTEGER,
    p_plan_id UUID DEFAULT NULL
)
RETURNS VOID AS $$
DECLARE
    v_current_expiry TIMESTAMPTZ;
    v_new_expiry TIMESTAMPTZ;
BEGIN
    SELECT expires_at INTO v_current_expiry 
    FROM premium_subscriptions 
    WHERE user_id = p_user_id AND status = 'active' 
    LIMIT 1;

    IF v_current_expiry IS NOT NULL AND v_current_expiry > NOW() THEN
        v_new_expiry := v_current_expiry + (p_days || ' days')::INTERVAL;
    ELSE
        v_new_expiry := NOW() + (p_days || ' days')::INTERVAL;
    END IF;

    INSERT INTO premium_subscriptions (user_id, plan_id, status, starts_at, expires_at, grant_history)
    VALUES (
        p_user_id, 
        p_plan_id, 
        'active', 
        NOW(), 
        v_new_expiry, 
        jsonb_build_array(jsonb_build_object('granted_at', NOW(), 'days', p_days, 'expires_at', v_new_expiry))
    )
    ON CONFLICT (id) DO UPDATE SET
        expires_at = v_new_expiry,
        status = 'active',
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;
