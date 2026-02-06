"""SQLAlchemy database service for user management and usage tracking."""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, 
    Index, select, update, func, desc, text
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    """User data model."""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    language = Column(String, default="uk")
    credits = Column(Integer, default=10)
    monthly_quota = Column(Integer, default=30)
    monthly_used = Column(Integer, default=0)
    is_premium = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    usage_history = relationship("UsageHistory", back_populates="user")

class UsageHistory(Base):
    """Video usage history model."""
    __tablename__ = "usage_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    video_id = Column(String, nullable=False)
    video_title = Column(String)
    video_url = Column(String)
    credits_used = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="usage_history")

# Create Index
Index("idx_usage_user_id", UsageHistory.user_id)

class DatabaseService:
    """SQLAlchemy-based user management and usage tracking."""
    
    DEFAULT_CREDITS = 10
    DEFAULT_MONTHLY_QUOTA = 30
    
    def __init__(self, db_url: str):
        """
        Initialize database service.
        
        Args:
            db_url: SQLAlchemy database URL
        """
        self.engine = create_async_engine(db_url)
        self.session_factory = async_sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        self._initialized = False
    
    async def initialize(self) -> None:
        """Create tables if they don't exist."""
        if self._initialized:
            return
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        self._initialized = True
        logger.info("Database initialized with SQLAlchemy")
    
    async def get_or_create_user(
        self, 
        user_id: int, 
        username: Optional[str] = None, 
        first_name: Optional[str] = None
    ) -> Any:
        """Get existing user or create new one."""
        await self.initialize()
        
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(User).where(User.user_id == user_id)
                )
                user = result.scalar_one_none()
                
                if user:
                    user.username = username or user.username
                    user.first_name = first_name or user.first_name
                    user.last_active = datetime.utcnow()
                    return user
                
                user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    credits=self.DEFAULT_CREDITS,
                    monthly_quota=self.DEFAULT_MONTHLY_QUOTA
                )
                session.add(user)
                
                logger.info(f"Created new user: {user_id} ({username})")
                return user
    
    async def check_credits(self, user_id: int) -> tuple[bool, int]:
        """Check if user has available credits."""
        await self.initialize()
        
        async with self.session_factory() as session:
            result = await session.execute(
                select(User.credits, User.is_blocked, User.is_premium)
                .where(User.user_id == user_id)
            )
            row = result.fetchone()
            
            if not row:
                return True, self.DEFAULT_CREDITS
            
            credits, is_blocked, is_premium = row
            
            if is_blocked:
                return False, 0
            
            if is_premium:
                return True, -1
            
            return credits > 0, credits
    
    async def use_credit(
        self, 
        user_id: int, 
        video_id: str, 
        video_title: str,
        video_url: str
    ) -> bool:
        """Use one credit and log usage."""
        await self.initialize()
        
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(User).where(User.user_id == user_id)
                )
                user = result.scalar_one_none()
                
                if not user or user.is_blocked:
                    return False
                
                if not user.is_premium:
                    if user.credits <= 0:
                        return False
                    user.credits -= 1
                    user.monthly_used += 1
                
                usage = UsageHistory(
                    user_id=user_id,
                    video_id=video_id,
                    video_title=video_title,
                    video_url=video_url
                )
                session.add(usage)
                
                logger.info(f"User {user_id} used credit for video {video_id}")
                return True
    
    async def get_user_stats(self, user_id: int) -> dict:
        """Get user statistics."""
        await self.initialize()
        
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            user = result.scalar_one_none()
            
            if not user:
                return {}
            
            count_result = await session.execute(
                select(func.count(UsageHistory.id)).where(UsageHistory.user_id == user_id)
            )
            total_videos = count_result.scalar()
            
            return {
                "user_id": user.user_id,
                "username": user.username,
                "credits": user.credits,
                "monthly_quota": user.monthly_quota,
                "monthly_used": user.monthly_used,
                "is_premium": user.is_premium,
                "total_videos": total_videos,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_active": user.last_active.isoformat() if user.last_active else None
            }
    
    async def add_credits(self, user_id: int, amount: int) -> bool:
        """Add credits to user account (admin function)."""
        await self.initialize()
        
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    update(User)
                    .where(User.user_id == user_id)
                    .values(credits=User.credits + amount)
                )
                return result.rowcount > 0
    
    async def set_premium(self, user_id: int, is_premium: bool) -> bool:
        """Set user premium status (admin function)."""
        await self.initialize()
        
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    update(User)
                    .where(User.user_id == user_id)
                    .values(is_premium=is_premium)
                )
                return result.rowcount > 0
    
    async def block_user(self, user_id: int, blocked: bool = True) -> bool:
        """Block or unblock user (admin function)."""
        await self.initialize()
        
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    update(User)
                    .where(User.user_id == user_id)
                    .values(is_blocked=blocked)
                )
                return result.rowcount > 0
    
    async def get_user_history(self, user_id: int, limit: int = 50) -> list[dict]:
        """Get user's video processing history."""
        await self.initialize()
        
        async with self.session_factory() as session:
            result = await session.execute(
                select(UsageHistory)
                .where(UsageHistory.user_id == user_id)
                .order_by(UsageHistory.created_at.desc())
                .limit(limit)
            )
            rows = result.scalars().all()
            
            return [
                {
                    "video_id": row.video_id,
                    "video_title": row.video_title,
                    "video_url": row.video_url,
                    "created_at": row.created_at.isoformat() if row.created_at else None
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
    
    async def get_all_users_stats(self, limit: int = 100) -> list[dict]:
        """Get statistics for all users (admin function)."""
        await self.initialize()
        
        async with self.session_factory() as session:
            # Subquery to count videos per user
            count_subquery = (
                select(UsageHistory.user_id, func.count(UsageHistory.id).label("total_videos"))
                .group_by(UsageHistory.user_id)
                .subquery()
            )
            
            # Join users with subquery
            query = (
                select(User, count_subquery.c.total_videos)
                .outerjoin(count_subquery, User.user_id == count_subquery.c.user_id)
                .order_by(User.last_active.desc())
                .limit(limit)
            )
            
            result = await session.execute(query)
            
            return [
                {
                    "user_id": user.user_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "credits": user.credits,
                    "monthly_used": user.monthly_used,
                    "is_premium": user.is_premium,
                    "is_blocked": user.is_blocked,
                    "total_videos": total_videos or 0,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_active": user.last_active.isoformat() if user.last_active else None
                }
                for user, total_videos in result
            ]
    
    async def get_total_stats(self) -> dict:
        """Get overall bot statistics (admin function)."""
        await self.initialize()
        
        async with self.session_factory() as session:
            # Total users
            total_users = await session.scalar(select(func.count(User.user_id)))
            
            # Active users (last 7 days)
            active_users = await session.scalar(
                select(func.count(User.user_id))
                .where(User.last_active > text("datetime('now', '-7 days')"))
            )
            # Note: For Postgres, the text above might need adjustment depending on the driver,
            # but usually datetime functions are similar. SQLAlchemy handles intervals too.
            # Let's use a more robust version:
            # from sqlalchemy import interval
            # active_users = await session.scalar(...)
            
            # Premium users
            premium_users = await session.scalar(
                select(func.count(User.user_id)).where(User.is_premium == True)
            )
            
            # Total videos processed
            total_videos = await session.scalar(select(func.count(UsageHistory.id)))
            
            # Videos today
            videos_today = await session.scalar(
                select(func.count(UsageHistory.id))
                .where(func.date(UsageHistory.created_at) == func.date(func.now()))
            )
            
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
        
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    update(User)
                    .where(User.user_id == user_id)
                    .values(language=lang)
                )
                return result.rowcount > 0
    
    async def get_language(self, user_id: int) -> str:
        """Get user language preference."""
        await self.initialize()
        
        async with self.session_factory() as session:
            result = await session.execute(
                select(User.language).where(User.user_id == user_id)
            )
            lang = result.scalar()
            return lang if lang else "uk"
