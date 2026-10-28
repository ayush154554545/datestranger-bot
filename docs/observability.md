# Observability & Structured Logging Specification

## 1. Overview
Observability in Date Stranger relies on structured Python logging (`logging` module), Flask health check endpoints, and Discord alerts.

---

## 2. Log Levels & Formatting Policy

```text
TIMESTAMP [LOG_LEVEL] [MODULE_NAME] Message payload (user_id=123, event=match_success)
```

* **`DEBUG`**: Internal state transitions, raw webhook payload dispatch.
* **`INFO`**: Match created, user registered, payment completed.
* **`WARNING`**: Retryable network timeout, stale queue entry cleaned.
* **`ERROR`**: Database query failure, Discord HTTP error.
* **`CRITICAL`**: Database connection lost, missing environment variable.

---

## 3. Health & Diagnostic Endpoints
* **URL Path**: `GET /`
* **Response**: `HTML 200 OK` ("Date Stranger Bot is Running!")
* **Purpose**: Used by Render / Fly.io container orchestrators for liveness probes.
