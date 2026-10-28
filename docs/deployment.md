# Deployment & Operations Guide — Date Stranger Bot

## 1. Containerization & Docker Setup
The bot service is containerized using `Dockerfile` (Python 3.11-slim base).

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

---

## 2. Deployment Configurations

### 2.1 Render (`render.yaml`)
* Runtime: `python` (Version 3.11)
* Service Type: Web Service (Health check endpoint provided by background Flask thread).
* Build Command: `pip install -r requirements.txt`
* Start Command: `python bot.py`

### 2.2 Fly.io (`fly.toml`)
* Container build using `Dockerfile` or `nixpacks.toml`.
* Auto-restart policy: `always`.

---

## 3. Production Deployment Checklist
1. Verify `BOT_TOKEN` and `SUPABASE_SERVICE_ROLE_KEY` environment variables are set in production environment settings.
2. Confirm Supabase database indexes and table constraints (`CHECK (age >= 18)`) are applied.
3. Verify web service health check returns HTTP 200 OK.
