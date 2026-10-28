"""
DateWithStranger Modular Application Entrypoint
"""

import sys
from datestranger.config.settings import get_settings
from datestranger.infrastructure.logging.logger import get_logger
from datestranger.infrastructure.redis.client import get_redis_client

logger = get_logger("main")


def initialize_app():
    settings = get_settings()
    logger.info(f"🚀 Initializing DateWithStranger in [{settings.env}] mode...")
    logger.info(f"🔒 Security Gate: 18+ Adult Service (Min Age: {settings.security.min_age})")

    # Initialize Redis Client
    redis_client = get_redis_client()
    if redis_client.is_connected():
        logger.info("⚡ Redis Infrastructure: ONLINE")
    else:
        logger.info("ℹ️ Redis Infrastructure: IN-MEMORY FALLBACK MODE")

    logger.info("✅ Core Application Package Restructuring Complete.")
    return True


if __name__ == "__main__":
    initialize_app()
