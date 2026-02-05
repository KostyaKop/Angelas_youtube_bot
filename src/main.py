"""Main entry point for the Telegram bot."""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import config
from src.handlers import commands, youtube, followup
from src.services.context_store import ContextStore
from src.services.ai_analyzer import AIAnalyzer
from src.services.youtube import YouTubeService
from src.services.sheets_logger import SheetsLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


async def main():
    """Initialize and start the bot."""
    
    # Validate configuration
    missing = config.validate()
    if missing:
        logger.error(f"Missing required configuration: {', '.join(missing)}")
        sys.exit(1)
    
    # Initialize services
    context_store = ContextStore(config.upstash_redis_url, config.redis_ttl)
    youtube_service = YouTubeService(config.apify_api_key)
    ai_analyzer = AIAnalyzer(config.gemini_api_key, config.openai_api_key)
    sheets_logger = SheetsLogger(config.google_sheets_id, config.google_service_account)
    
    # Initialize bot
    bot = Bot(
        token=config.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Inject dependencies
    dp["context_store"] = context_store
    dp["youtube_service"] = youtube_service
    dp["ai_analyzer"] = ai_analyzer
    dp["sheets_logger"] = sheets_logger
    dp["config"] = config
    
    # Register handlers
    dp.include_router(commands.router)
    dp.include_router(youtube.router)
    dp.include_router(followup.router)
    
    # Start polling
    logger.info("Starting bot...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
