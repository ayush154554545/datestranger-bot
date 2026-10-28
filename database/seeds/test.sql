-- ============================================================================
-- TEST SEED DATA (ISOLATED FIXTURE FOR AUTOMATED SUITES)
-- ============================================================================

INSERT INTO users (id, telegram_user_id, telegram_username, first_name, account_status, eligibility_status)
VALUES 
    ('90000000-0000-0000-0000-000000000001', 999000001, 'test_user_1', 'TestUser1', 'active', 'eligible'),
    ('90000000-0000-0000-0000-000000000002', 999000002, 'test_user_2', 'TestUser2', 'active', 'eligible')
ON CONFLICT (telegram_user_id) DO NOTHING;

INSERT INTO profiles (user_id, display_name, age, gender)
VALUES 
    ('90000000-0000-0000-0000-000000000001', 'TestUser1', 20, 'female'),
    ('90000000-0000-0000-0000-000000000002', 'TestUser2', 25, 'male')
ON CONFLICT (user_id) DO NOTHING;
