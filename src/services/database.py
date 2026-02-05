"""SQLite database service for user management and usage tracking."""

import logging
import aiosqlite
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class User:
    """User data model."""
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    language: str = "uk"
    credits: int = 10
    monthly_quota: int = 30
    monthly_used: int = 0
    is_premium: bool = False
    is_blocked: bool = False
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None


class DatabaseService:
    """SQLite-based user management and usage tracking."""
    
    DEFAULT_CREDITS = 10
    DEFAULT_MONTHLY_QUOTA = 30
    
    def __init__(self, db_path: str = "data/bot.db"):
        """
        Initialize database service.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False
    
    async def initialize(self) -> None:
        """Create tables if they don't exist."""
        if self._initialized:
            return
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    language TEXT DEFAULT 'uk',
                    credits INTEGER DEFAULT 10,
                    monthly_quota INTEGER DEFAULT 30,
                    monthly_used INTEGER DEFAULT 0,
                    is_premium BOOLEAN DEFAULT FALSE,
                    is_blocked BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS usage_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    video_id TEXT NOT NULL,
                    video_title TEXT,
                    video_url TEXT,
                    credits_used INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Index for faster user lookups
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_usage_user_id 
                ON usage_history(user_id)
            """)
            
            await db.commit()
        
        self._initialized = True
        logger.info(f"Database initialized at {self.db_path}")
    
    async def get_or_create_user(
        self, 
        user_id: int, 
        username: Optional[str] = None, 
        first_name: Optional[str] = None
    ) -> User:
        """
        Get existing user or create new one.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            
        Returns:
            User object
        """
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Try to get existing user
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                # Update last_active and username if changed
                await db.execute("""
                    UPDATE users 
                    SET last_active = CURRENT_TIMESTAMP,
                        username = COALESCE(?, username),
                        first_name = COALESCE(?, first_name)
                    WHERE user_id = ?
                """, (username, first_name, user_id))
                await db.commit()
                
                return User(
                    user_id=row["user_id"],
                    username=row["username"],
                    first_name=row["first_name"],
                    language=row["language"],
                    credits=row["credits"],
                    monthly_quota=row["monthly_quota"],
                    monthly_used=row["monthly_used"],
                    is_premium=bool(row["is_premium"]),
                    is_blocked=bool(row["is_blocked"]),
                    created_at=row["created_at"],
                    last_active=row["last_active"]
                )
            
            # Create new user
            await db.execute("""
                INSERT INTO users (user_id, username, first_name, credits, monthly_quota)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, first_name, self.DEFAULT_CREDITS, self.DEFAULT_MONTHLY_QUOTA))
            await db.commit()
            
            logger.info(f"Created new user: {user_id} ({username})")
            
            return User(
                user_id=user_id,
                username=username,
                first_name=first_name,
                credits=self.DEFAULT_CREDITS,
                monthly_quota=self.DEFAULT_MONTHLY_QUOTA,
                created_at=datetime.utcnow(),
                last_active=datetime.utcnow()
            )
    
    async def check_credits(self, user_id: int) -> tuple[bool, int]:
        """
        Check if user has available credits.
        
        Returns:
            Tuple of (has_credits, remaining_credits)
        """
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT credits, is_blocked, is_premium FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return True, self.DEFAULT_CREDITS  # New user will be created
            
            credits, is_blocked, is_premium = row
            
            if is_blocked:
                return False, 0
            
            if is_premium:
                return True, -1  # Unlimited
            
            return credits > 0, credits
    
    async def use_credit(
        self, 
        user_id: int, 
        video_id: str, 
        video_title: str,
        video_url: str
    ) -> bool:
        """
        Use one credit and log usage.
        
        Returns:
            True if credit was used, False if no credits available
        """
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            # Get current credits
            cursor = await db.execute(
                "SELECT credits, is_premium, is_blocked FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return False
            
            credits, is_premium, is_blocked = row
            
            if is_blocked:
                return False
            
            # Premium users don't consume credits
            if not is_premium:
                if credits <= 0:
                    return False
                
                # Decrement credits
                await db.execute(
                    "UPDATE users SET credits = credits - 1, monthly_used = monthly_used + 1 WHERE user_id = ?",
                    (user_id,)
                )
            
            # Log usage
            await db.execute("""
                INSERT INTO usage_history (user_id, video_id, video_title, video_url)
                VALUES (?, ?, ?, ?)
            """, (user_id, video_id, video_title, video_url))
            
            await db.commit()
            
            logger.info(f"User {user_id} used credit for video {video_id}")
            return True
    
    async def get_user_stats(self, user_id: int) -> dict:
        """Get user statistics."""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # User info
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            )
            user_row = await cursor.fetchone()
            
            if not user_row:
                return {}
            
            # Count total videos processed
            cursor = await db.execute(
                "SELECT COUNT(*) FROM usage_history WHERE user_id = ?",
                (user_id,)
            )
            total_videos = (await cursor.fetchone())[0]
            
            return {
                "user_id": user_row["user_id"],
                "username": user_row["username"],
                "credits": user_row["credits"],
                "monthly_quota": user_row["monthly_quota"],
                "monthly_used": user_row["monthly_used"],
                "is_premium": bool(user_row["is_premium"]),
                "total_videos": total_videos,
                "created_at": user_row["created_at"],
                "last_active": user_row["last_active"]
            }
    
    async def add_credits(self, user_id: int, amount: int) -> bool:
        """Add credits to user account (admin function)."""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            result = await db.execute(
                "UPDATE users SET credits = credits + ? WHERE user_id = ?",
                (amount, user_id)
            )
            await db.commit()
            
            if result.rowcount > 0:
                logger.info(f"Added {amount} credits to user {user_id}")
                return True
            return False
    
    async def set_premium(self, user_id: int, is_premium: bool) -> bool:
        """Set user premium status (admin function)."""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            result = await db.execute(
                "UPDATE users SET is_premium = ? WHERE user_id = ?",
                (is_premium, user_id)
            )
            await db.commit()
            return result.rowcount > 0
    
    async def block_user(self, user_id: int, blocked: bool = True) -> bool:
        """Block or unblock user (admin function)."""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            result = await db.execute(
                "UPDATE users SET is_blocked = ? WHERE user_id = ?",
                (blocked, user_id)
            )
            await db.commit()
            return result.rowcount > 0
    
    async def get_user_history(self, user_id: int, limit: int = 50) -> list[dict]:
        """Get user's video processing history."""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute("""
                SELECT video_id, video_title, video_url, created_at
                FROM usage_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            rows = await cursor.fetchall()
            
            return [
                {
                    "video_id": row["video_id"],
                    "video_title": row["video_title"],
                    "video_url": row["video_url"],
                    "created_at": row["created_at"]
                }
                for row in rows
            ]
    
    async def export_history_csv(self, user_id: int) -> str:
        """Export user history as CSV string."""
        history = await self.get_user_history(user_id, limit=1000)
        
        if not history:
            return ""
        
        lines = ["Date,Video Title,URL"]
        for item in history:
            title = item["video_title"].replace(",", ";") if item["video_title"] else ""
            url = item["video_url"] or ""
            date = item["created_at"] or ""
            lines.append(f"{date},{title},{url}")
        
        return "\n".join(lines)
    
    # ========== Admin functions ==========
    
    async def get_all_users_stats(self, limit: int = 100) -> list[dict]:
        """Get statistics for all users (admin function)."""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute("""
                SELECT 
                    u.*,
                    (SELECT COUNT(*) FROM usage_history WHERE user_id = u.user_id) as total_videos
                FROM users u
                ORDER BY u.last_active DESC
                LIMIT ?
            """, (limit,))
            
            rows = await cursor.fetchall()
            
            return [
                {
                    "user_id": row["user_id"],
                    "username": row["username"],
                    "first_name": row["first_name"],
                    "credits": row["credits"],
                    "monthly_used": row["monthly_used"],
                    "is_premium": bool(row["is_premium"]),
                    "is_blocked": bool(row["is_blocked"]),
                    "total_videos": row["total_videos"],
                    "created_at": row["created_at"],
                    "last_active": row["last_active"]
                }
                for row in rows
            ]
    
    async def get_total_stats(self) -> dict:
        """Get overall bot statistics (admin function)."""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            # Total users
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            total_users = (await cursor.fetchone())[0]
            
            # Active users (last 7 days)
            cursor = await db.execute("""
                SELECT COUNT(*) FROM users 
                WHERE last_active > datetime('now', '-7 days')
            """)
            active_users = (await cursor.fetchone())[0]
            
            # Premium users
            cursor = await db.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1")
            premium_users = (await cursor.fetchone())[0]
            
            # Total videos processed
            cursor = await db.execute("SELECT COUNT(*) FROM usage_history")
            total_videos = (await cursor.fetchone())[0]
            
            # Videos today
            cursor = await db.execute("""
                SELECT COUNT(*) FROM usage_history 
                WHERE date(created_at) = date('now')
            """)
            videos_today = (await cursor.fetchone())[0]
            
            return {
                "total_users": total_users,
                "active_users_7d": active_users,
                "premium_users": premium_users,
                "total_videos": total_videos,
                "videos_today": videos_today
            }
    
    async def set_language(self, user_id: int, lang: str) -> bool:
        """Set user language preference."""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            result = await db.execute(
                "UPDATE users SET language = ? WHERE user_id = ?",
                (lang, user_id)
            )
            await db.commit()
            return result.rowcount > 0
    
    async def get_language(self, user_id: int) -> str:
        """Get user language preference."""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT language FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            return row[0] if row else "uk"
