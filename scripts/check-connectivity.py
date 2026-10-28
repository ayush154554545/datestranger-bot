#!/usr/bin/env python3
"""
DateWithStranger Safe Connectivity Verification Script (Phase 0)

Verifies connectivity to configured infrastructure components (Telegram, Supabase, Redis, Discord).
NEVER mutates production data and NEVER exposes secret values.
"""

import os
import sys
import argparse
import requests
from dotenv import load_dotenv

# Ensure stdout uses UTF-8 encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment
load_dotenv(dotenv_path=".env", override=True)
load_dotenv(dotenv_path="bot/.env", override=False)


def check_telegram() -> bool:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token or "your-telegram" in token:
        print("  [FAIL] Telegram: BOT_TOKEN missing or placeholder", flush=True)
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200 and resp.json().get("ok"):
            bot_info = resp.json().get("result", {})
            username = bot_info.get("username", "Unknown")
            print(f"  [PASS] Telegram: Connected successfully to @{username}", flush=True)
            return True
        else:
            print(f"  [FAIL] Telegram: API returned HTTP {resp.status_code}", flush=True)
            return False
    except Exception as e:
        print(f"  [FAIL] Telegram: Connection failed ({e})", flush=True)
        return False


def check_supabase() -> bool:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key or "your-supabase" in url:
        print("  [FAIL] Supabase: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing or placeholder", flush=True)
        return False
    try:
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}"
        }
        endpoint = f"{url.rstrip('/')}/rest/v1/"
        resp = requests.get(endpoint, headers=headers, timeout=3)
        if resp.status_code in [200, 204]:
            print("  [PASS] Supabase: REST API reachable & Service Role Key authenticated", flush=True)
            return True
        else:
            print(f"  [FAIL] Supabase: API returned HTTP {resp.status_code}", flush=True)
            return False
    except Exception as e:
        print(f"  [FAIL] Supabase: Connection failed ({e})", flush=True)
        return False


def check_redis() -> bool:
    try:
        import redis
        host = os.getenv("REDIS_HOST", "localhost").strip()
        port = int(os.getenv("REDIS_PORT", "6379"))
        password = os.getenv("REDIS_PASSWORD", None)
        redis_url = os.getenv("REDIS_URL", None)

        if redis_url and not "localhost" in redis_url:
            r = redis.Redis.from_url(redis_url, socket_timeout=2)
        else:
            r = redis.Redis(host=host, port=port, password=password, socket_timeout=2)

        ping_ok = r.ping()
        if ping_ok:
            print(f"  [PASS] Redis: Connection ONLINE (PING responded PONG)", flush=True)
            return True
        else:
            print(f"  [FAIL] Redis: Connection PING failed", flush=True)
            return False
    except ImportError:
        print("  [INFO] Redis: redis library not installed in runtime environment; in-memory fallback active", flush=True)
        return False
    except Exception as e:
        print(f"  [INFO] Redis: Service OFFLINE ({e}); in-memory fallback mode active", flush=True)
        return False


def check_discord() -> bool:
    webhook_url = os.getenv("STATUS_WEBHOOK", "").strip()
    if not webhook_url or "your-discord" in webhook_url:
        print("  [INFO] Discord: STATUS_WEBHOOK missing or placeholder", flush=True)
        return False
    try:
        resp = requests.get(webhook_url, timeout=3)
        if resp.status_code == 200:
            name = resp.json().get("name", "Webhook Channel")
            print(f"  [PASS] Discord: STATUS_WEBHOOK reachable (Channel: '{name}')", flush=True)
            return True
        else:
            print(f"  [FAIL] Discord: Webhook returned HTTP {resp.status_code}", flush=True)
            return False
    except Exception as e:
        print(f"  [FAIL] Discord: Connection failed ({e})", flush=True)
        return False


def main():
    parser = argparse.ArgumentParser(description="DateWithStranger Connectivity Checker")
    parser.add_argument("--service", choices=["all", "telegram", "supabase", "redis", "discord"], default="all")
    args = parser.parse_args()

    print("=" * 65, flush=True)
    print("DateWithStranger Infrastructure Connectivity Verification", flush=True)
    print("=" * 65, flush=True)

    results = []

    if args.service in ["all", "telegram"]:
        results.append(check_telegram())

    if args.service in ["all", "supabase"]:
        results.append(check_supabase())

    if args.service in ["all", "redis"]:
        results.append(check_redis())

    if args.service in ["all", "discord"]:
        results.append(check_discord())

    print("=" * 65, flush=True)
    if any(results):
        print("Status: Verified active infrastructure connectivity.", flush=True)
    else:
        print("Status: No active external connections verified.", flush=True)
    print("=" * 65, flush=True)


if __name__ == "__main__":
    main()
