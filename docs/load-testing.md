# Load Testing Strategy & Benchmarks

## 1. Load Testing Framework
Uses `Locust` / `k6` to simulate high-concurrency Telegram API webhooks, matching requests, and API endpoints.

---

## 2. Load Testing Tiers
* **Tier 1 (100 Users)**: Baseline response latency validation.
* **Tier 2 (250 Users)**: Concurrent matching queue load check.
* **Tier 3 (500 Users)**: DB connection pool stress check.
* **Tier 4 (1,000 Concurrent Users)**: Target peak concurrency stress test.

---

## 3. Mandatory Reporting Classification
All load test reports must distinguish:
- **Designed for**: 50,000+ registered users / 1,000 concurrent active users.
- **Tested at**: Execution load level.
- **Verified at**: Empirical pass level.
- **Not yet verified**: Un-tested tiers.
