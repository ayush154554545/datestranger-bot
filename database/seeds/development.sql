-- ============================================================================
-- DEVELOPMENT SEED DATA (SYNTHETIC ONLY - NO REAL USER DATA)
-- ============================================================================

-- 1. Synthetic Users
INSERT INTO users (id, telegram_user_id, telegram_username, first_name, last_name, language_code, account_status, eligibility_status)
VALUES 
    ('10000000-0000-0000-0000-000000000001', 990000001, 'synth_alice', 'Alice', 'Doe', 'en', 'active', 'eligible'),
    ('10000000-0000-0000-0000-000000000002', 990000002, 'synth_bob', 'Bob', 'Smith', 'en', 'active', 'eligible'),
    ('10000000-0000-0000-0000-000000000003', 990000003, 'synth_charlie', 'Charlie', 'Brown', 'es', 'active', 'eligible')
ON CONFLICT (telegram_user_id) DO NOTHING;

-- 2. Synthetic Profiles (All 18+)
INSERT INTO profiles (user_id, display_name, bio, age, gender, country, language, profile_status)
VALUES 
    ('10000000-0000-0000-0000-000000000001', 'Alice', 'Loves coffee and books', 24, 'female', 'US', 'en', 'complete'),
    ('10000000-0000-0000-0000-000000000002', 'Bob', 'Tech enthusiast & gamer', 27, 'male', 'US', 'en', 'complete'),
    ('10000000-0000-0000-0000-000000000003', 'Charlie', 'Hola a todos!', 22, 'male', 'ES', 'es', 'complete')
ON CONFLICT (user_id) DO NOTHING;

-- 3. Synthetic Preferences
INSERT INTO user_preferences (user_id, preferred_gender, min_age, max_age, preferred_country, preferred_language)
VALUES 
    ('10000000-0000-0000-0000-000000000001', 'male', 20, 35, 'any', 'en'),
    ('10000000-0000-0000-0000-000000000002', 'female', 18, 30, 'any', 'en'),
    ('10000000-0000-0000-0000-000000000003', 'any', 18, 99, 'any', 'any')
ON CONFLICT (user_id) DO NOTHING;

-- 4. Premium Plans
INSERT INTO premium_plans (id, code, name, duration_days, price_stars, is_active)
VALUES 
    ('20000000-0000-0000-0000-000000000001', 'WEEKLY_STARS', '7 Days Premium', 7, 50, TRUE),
    ('20000000-0000-0000-0000-000000000002', 'MONTHLY_STARS', '30 Days Premium', 30, 150, TRUE)
ON CONFLICT (code) DO NOTHING;
