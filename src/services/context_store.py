"""Redis context store for user video sessions."""

import json
import logging
from urllib.parse import urlparse

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class ContextStore:
    """Redis-based context storage for video analysis sessions."""
    
    KEY_PREFIX = "youtube_context"
    
    def __init__(self, redis_url: str, ttl: int = 86400):
        """
        Initialize Redis connection.
        
        Args:
            redis_url: Upstash Redis URL
            ttl: Time-to-live in seconds (default: 24 hours)
        """
        self.redis_url = redis_url
        self.ttl = ttl
        self._client = None
    
    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._client is None:
            self._client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._client
    
    def _make_key(self, user_id: int) -> str:
        """Generate Redis key for user."""
        return f"{self.KEY_PREFIX}:{user_id}"
    
    async def save(self, user_id: int, data: dict) -> None:
        """
        Save video context for user.
        Overwrites any existing context.
        
        Args:
            user_id: Telegram user ID
            data: Context data (video_url, transcript, summary, etc.)
        """
        try:
            client = await self._get_client()
            key = self._make_key(user_id)
            
            await client.setex(
                key,
                self.ttl,
                json.dumps(data, ensure_ascii=False)
            )
            
            logger.debug(f"Saved context for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to save context for user {user_id}: {e}")
    
    async def get(self, user_id: int) -> dict | None:
        """
        Get video context for user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Context dict or None if not found/expired
        """
        try:
            client = await self._get_client()
            key = self._make_key(user_id)
            
            data = await client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get context for user {user_id}: {e}")
            return None
    
    async def delete(self, user_id: int) -> None:
        """
        Delete video context for user.
        
        Args:
            user_id: Telegram user ID
        """
        try:
            client = await self._get_client()
            key = self._make_key(user_id)
            
            await client.delete(key)
            logger.debug(f"Deleted context for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to delete context for user {user_id}: {e}")
    
    async def exists(self, user_id: int) -> bool:
        """Check if user has active context."""
        try:
            client = await self._get_client()
            key = self._make_key(user_id)
            
            return await client.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check context for user {user_id}: {e}")
            return False
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
