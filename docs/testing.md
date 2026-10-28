# Comprehensive Testing Framework & Matrix

## 1. Testing Philosophy & Strict Rule
**No code change will be accepted without automated and manual verification.**

---

## 2. 12-Step Change Verification Workflow
Before submitting any implementation change, the developer/agent MUST execute the following workflow:

1. **Step 1**: Explain exact change scope.
2. **Step 2**: Identify affected modules.
3. **Step 3**: List possible regression risks.
4. **Step 4**: Implement code modifications.
5. **Step 5**: Run code linting & syntax checks (`flake8` / `black`).
6. **Step 6**: Execute relevant unit tests (`pytest tests/unit`).
7. **Step 7**: Execute integration tests (`pytest tests/integration`).
8. **Step 8**: Execute database tests (`pytest tests/database`).
9. **Step 9**: Execute security checks (Verify 18+ gate & secret protection).
10. **Step 10**: Perform application startup validation (`python -m bot.src.datestranger.main`).
11. **Step 11**: Perform manual Telegram flow verification.
12. **Step 12**: Output empirical test report table.

---

## 3. Comprehensive Test Matrix

### 3.1 Startup & Configuration Tests
* Missing `BOT_TOKEN` environment variable.
* Invalid `SUPABASE_SERVICE_ROLE_KEY`.
* Database connection failure handling.

### 3.2 Signup & 18+ Age Gate Tests
* Valid adult signup (Age 25) -> Success.
* Minor signup attempt (Age 17) -> Rejection.
* Boundary signup attempt (Age 18) -> Success.
* Duplicate signup attempt -> Idempotent profile return.

### 3.3 Matching Engine Tests
* Priority ordering (Admin > Premium > Free).
* Mutual gender filter matching.
* Mutual age filter bounds matching.
* Double-match race condition prevention under concurrent requests.
* Stale queue entry removal.

### 3.4 Payment & Stars Idempotency Tests
* Valid invoice pre-checkout validation.
* Successful purchase granting premium.
* Replayed duplicate `charge_id` -> Rejected without double credit.
* Plan stacking (Week + Month).

### 3.5 Referral Subsystem Tests
* Valid referral attribution (5 invites -> +1 Day Premium).
* Self-referral attempt -> Rejection.
* Uncompleted profile referral attempt -> Deferred credit.

---

## 4. Test Environments
* **Development**: Local environment with dedicated Supabase dev project.
* **Testing**: Automated CI test execution against test database.
* **Production**: Real bot deployment. (Never run destructive tests in production).
