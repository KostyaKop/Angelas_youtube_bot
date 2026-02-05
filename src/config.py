"""Configuration management for the bot."""

import os
import json
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Application configuration from environment variables."""
    
    # Telegram
    telegram_bot_token: str
    
    # AI Models
    gemini_api_key: str
    openai_api_key: str
    
    # Redis
    upstash_redis_url: str
    
    # Google Sheets
    google_sheets_id: str
    google_service_account: dict
    
    # Apify
    apify_api_key: str
    
    # Optional
    admin_user_id: int | None = None
    
    # Constants
    redis_ttl: int = 86400  # 24 hours
    max_message_length: int = 4000
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        
        # Parse Google service account JSON
        service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "{}")
        try:
            google_service_account = json.loads(service_account_json)
        except json.JSONDecodeError:
            google_service_account = {}
        
        # Parse admin user ID
        admin_id_str = os.getenv("ADMIN_USER_ID")
        admin_user_id = int(admin_id_str) if admin_id_str else None
        
        return cls(
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            upstash_redis_url=os.getenv("UPSTASH_REDIS_URL", ""),
            google_sheets_id=os.getenv("GOOGLE_SHEETS_ID", ""),
            google_service_account=google_service_account,
            apify_api_key=os.getenv("APIFY_API_KEY", ""),
            admin_user_id=admin_user_id,
        )
    
    def validate(self) -> list[str]:
        """Validate required configuration. Returns list of missing fields."""
        missing = []
        if not self.telegram_bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not self.upstash_redis_url:
            missing.append("UPSTASH_REDIS_URL")
        if not self.apify_api_key:
            missing.append("APIFY_API_KEY")
        return missing


# Global config instance
config = Config.from_env()
