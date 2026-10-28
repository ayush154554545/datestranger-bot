#!/usr/bin/env python3
"""
DateWithStranger Safe Environment Validation Script (Phase 0)

Checks required environment variables for presence, placeholder values, and formatting.
NEVER prints or exposes secret values.
"""

import os
import sys
import re
from urllib.parse import urlparse
from typing import List, Tuple
from dotenv import load_dotenv

# Ensure stdout uses UTF-8 encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load .env file
load_dotenv(dotenv_path=".env", override=True)
load_dotenv(dotenv_path="bot/.env", override=False)

PLACEHOLDER_SUBSTRINGS = [
    "your-",
    "change_me",
    "xxxx",
    "example",
    "placeholder",
    "0000000000"
]


def is_placeholder(value: str) -> bool:
    if not value:
        return True
    val_lower = value.lower()
    return any(p in val_lower for p in PLACEHOLDER_SUBSTRINGS)


def validate_url(url: str) -> bool:
    if not url or is_placeholder(url):
        return False
    try:
        result = urlparse(url)
        return all([result.scheme in ["http", "https", "mongodb", "mongodb+srv", "redis", "rediss", "postgres", "postgresql"], result.netloc])
    except Exception:
        return False


def run_env_check() -> bool:
    print("=" * 65)
    print("DateWithStranger Environment Check")
    print("=" * 65)

    checks: List[Tuple[str, str, bool, str]] = []

    # 1. Telegram BOT_TOKEN
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token or is_placeholder(bot_token):
        checks.append(("Telegram BOT_TOKEN", "BOT_TOKEN", False, "Missing or placeholder"))
    elif not re.match(r"^\d+:[A-Za-z0-9_-]{35,}$", bot_token):
        checks.append(("Telegram BOT_TOKEN", "BOT_TOKEN", False, "Invalid format"))
    else:
        checks.append(("Telegram BOT_TOKEN", "BOT_TOKEN", True, "Configured"))

    # 2. Telegram ADMIN_ID
    admin_id = os.getenv("ADMIN_ID", "").strip()
    if not admin_id or is_placeholder(admin_id):
        checks.append(("Telegram ADMIN_ID", "ADMIN_ID", False, "Missing or placeholder"))
    elif not admin_id.isdigit():
        checks.append(("Telegram ADMIN_ID", "ADMIN_ID", False, "Must be numeric Telegram ID"))
    else:
        checks.append(("Telegram ADMIN_ID", "ADMIN_ID", True, "Configured"))

    # 3. Supabase URL
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    if validate_url(supabase_url):
        checks.append(("Supabase URL", "SUPABASE_URL", True, "Configured"))
    else:
        checks.append(("Supabase URL", "SUPABASE_URL", False, "Missing or invalid Supabase URL"))

    # 4. Supabase Service Role Key
    supabase_sr_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not supabase_sr_key or is_placeholder(supabase_sr_key):
        checks.append(("Supabase Service Role Key", "SUPABASE_SERVICE_ROLE_KEY", False, "Missing or placeholder"))
    elif not (supabase_sr_key.startswith("eyJ") or supabase_sr_key.startswith("sbp_") or len(supabase_sr_key) >= 30):
        checks.append(("Supabase Service Role Key", "SUPABASE_SERVICE_ROLE_KEY", False, "Invalid key format"))
    else:
        checks.append(("Supabase Service Role Key", "SUPABASE_SERVICE_ROLE_KEY", True, "Configured"))

    # 5. Redis Host / URL
    redis_url = os.getenv("REDIS_URL", "").strip()
    redis_host = os.getenv("REDIS_HOST", "").strip()
    if (redis_url and validate_url(redis_url)) or (redis_host and not is_placeholder(redis_host)):
        checks.append(("Redis Connection", "REDIS_URL / REDIS_HOST", True, "Configured"))
    else:
        checks.append(("Redis Connection", "REDIS_URL / REDIS_HOST", False, "Missing or placeholder (In-memory fallback mode active)"))

    # 6. Legacy MongoDB URL
    mongo_url = os.getenv("MONGO_URL", "").strip()
    if mongo_url and not is_placeholder(mongo_url) and ("mongodb" in mongo_url):
        checks.append(("Legacy MongoDB URL", "MONGO_URL", True, "Configured (Read-only migration source)"))
    else:
        checks.append(("Legacy MongoDB URL", "MONGO_URL", False, "Not configured (Required only for legacy data migration)"))

    # 7. Cloudflare R2 Credentials
    r2_key = os.getenv("R2_ACCESS_KEY_ID", "").strip()
    r2_secret = os.getenv("R2_SECRET_ACCESS_KEY", "").strip()
    if r2_key and r2_secret and not is_placeholder(r2_key) and not is_placeholder(r2_secret):
        checks.append(("Cloudflare R2 Storage", "R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY", True, "Configured"))
    else:
        checks.append(("Cloudflare R2 Storage", "R2_ACCESS_KEY_ID", False, "Not configured (Optional for Phase 0)"))

    # 8. Discord Webhooks
    status_webhook = os.getenv("STATUS_WEBHOOK", "").strip()
    if status_webhook and validate_url(status_webhook) and "discord.com" in status_webhook:
        checks.append(("Discord Status Webhook", "STATUS_WEBHOOK", True, "Configured"))
    else:
        checks.append(("Discord Status Webhook", "STATUS_WEBHOOK", False, "Not configured or placeholder"))

    # Print results safely
    all_passed = True
    for label, var_name, passed, detail in checks:
        status_tag = "[PASS]" if passed else "[FAIL]"
        print(f"  {status_tag:<7} {label:<28} ({var_name}): {detail}")
        if not passed and var_name in ["BOT_TOKEN", "ADMIN_ID", "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]:
            all_passed = False

    print("=" * 65)
    if all_passed:
        print("Result: READY FOR PHASE 0 VERIFICATION")
    else:
        print("Result: NOT READY — Mandatory credentials missing or invalid")
    print("=" * 65)

    return all_passed


if __name__ == "__main__":
    success = run_env_check()
    sys.exit(0 if success else 1)
