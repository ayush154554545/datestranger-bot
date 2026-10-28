# Known Issues & Technical Debt Inventory

## 1. Overview
This inventory lists known issues, architectural flaws, security risks, and technical debt discovered during the initial source code audit of `bot.py`.

---

## 2. Issue Inventory

### 2.1 Security Concerns
* **SEC-01 (Confirmed Safety Bug)**: Insecure age gate in legacy source (`MIN_AGE = 13`). Allows minors to register and match. Must be replaced with mandatory 18+ enforcement.

### 2.2 Architectural Problems
* **ARCH-01 (Monolithic File)**: Entire codebase resides in a single 4,540-line `bot.py` file without modular separation.
* **ARCH-02 (In-Memory Locks)**: Matching queue lock (`match_lock = Lock()`) is in-memory only. Horizontal deployment across container replicas causes race conditions and double-matching.
* **ARCH-03 (Volatile Session State)**: `admin_states`, `watching_state`, and `log_buffer` are stored in RAM. Container restarts wipe active admin session states and unflushed chat log buffers.

### 2.3 Technical Debt
* **DEBT-01 (Legacy Database)**: Coupled directly to MongoDB / PyMongo. Requires migration to Supabase (PostgreSQL).
* **DEBT-02 (Missing Automated Test Coverage)**: Zero automated unit, integration, or database tests present in legacy workspace.
* **DEBT-03 (Direct Webhook Coupling)**: Discord webhooks are invoked inline across handler threads without retry queues or dead-letter storage.
