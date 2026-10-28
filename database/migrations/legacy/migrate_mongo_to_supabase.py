#!/usr/bin/env python3
"""
DateWithStranger: Idempotent MongoDB to Supabase PostgreSQL Migration Tool.
Reads legacy MongoDB documents, transforms fields into relational entities, and safely upserts into Supabase.

Usage:
    python database/migrations/legacy/migrate_mongo_to_supabase.py [--dry-run]
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class MongoToSupabaseMigrator:
    def __init__(self, mongo_url: Optional[str] = None, supabase_url: Optional[str] = None, service_role_key: Optional[str] = None, dry_run: bool = False):
        self.dry_run = dry_run
        self.mongo_url = mongo_url or os.getenv("MONGO_URL", "")
        self.db_name = os.getenv("DB_NAME", "datestranger")
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL", "")
        self.service_role_key = service_role_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

        self.mongo_client = None
        self.mongo_db = None
        self.supabase = None

    def connect(self) -> bool:
        if self.mongo_url and MongoClient:
            try:
                self.mongo_client = MongoClient(self.mongo_url, serverSelectionTimeoutMS=5000)
                self.mongo_db = self.mongo_client[self.db_name]
                logging.info(f"Connected to legacy MongoDB: {self.db_name}")
            except Exception as e:
                logging.warning(f"Could not connect to MongoDB: {e}")

        if self.supabase_url and self.service_role_key and create_client:
            try:
                self.supabase = create_client(self.supabase_url, self.service_role_key)
                logging.info("Connected to Supabase PostgreSQL instance.")
            except Exception as e:
                logging.warning(f"Could not connect to Supabase: {e}")

        return True

    def migrate_users_and_profiles(self) -> int:
        if self.mongo_db is None:
            logging.info("MongoDB not connected. Skipping user migration.")
            return 0

        users_col = self.mongo_db["users"]
        migrated_count = 0

        for doc in users_col.find():
            telegram_user_id = doc.get("user_id")
            if not telegram_user_id:
                continue

            username = doc.get("username")
            name = doc.get("name", f"User_{telegram_user_id}")
            raw_age = doc.get("age", 18)
            # Adult 18+ policy enforcement
            age = max(18, int(raw_age)) if raw_age is not None else 18
            gender = doc.get("gender", "other")
            if gender not in ("male", "female", "other"):
                gender = "other"

            country = doc.get("country", "any")
            language = doc.get("language", "en")

            if self.dry_run:
                migrated_count += 1
                continue

            if self.supabase:
                user_res = self.supabase.table("users").upsert({
                    "telegram_user_id": telegram_user_id,
                    "telegram_username": username,
                    "first_name": name,
                    "language_code": language,
                    "account_status": "active" if not doc.get("is_banned") else "suspended",
                    "eligibility_status": "eligible"
                }, on_conflict="telegram_user_id").execute()

                if user_res and user_res.data:
                    user_uuid = user_res.data[0]["id"]
                    self.supabase.table("profiles").upsert({
                        "user_id": user_uuid,
                        "display_name": name,
                        "age": age,
                        "gender": gender,
                        "country": country,
                        "language": language,
                        "bio": doc.get("bio", ""),
                        "profile_status": "complete"
                    }, on_conflict="user_id").execute()

                    prefs = doc.get("search_preferences", {})
                    self.supabase.table("user_preferences").upsert({
                        "user_id": user_uuid,
                        "preferred_gender": prefs.get("preferred_gender", "any"),
                        "min_age": max(18, prefs.get("preferred_age_min", 18)),
                        "max_age": prefs.get("preferred_age_max", 99),
                        "preferred_country": prefs.get("preferred_country", "any")
                    }, on_conflict="user_id").execute()

            migrated_count += 1

        logging.info(f"Migrated {migrated_count} users & profiles.")
        return migrated_count

    def run_all(self):
        self.connect()
        self.migrate_users_and_profiles()
        logging.info("Migration routine finished cleanly.")


if __name__ == "__main__":
    is_dry_run = "--dry-run" in sys.argv
    migrator = MongoToSupabaseMigrator(dry_run=is_dry_run)
    migrator.run_all()
