"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import redis
from loguru import logger

from app.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    # For SQLite compatibility (if needed for development)
    poolclass=StaticPool if "sqlite" in settings.DATABASE_URL else None,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Redis connection
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    # Test connection
    redis_client.ping()
    logger.info("Redis connection established successfully")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    redis_client = None


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis() -> redis.Redis:
    """
    Get Redis client
    """
    if redis_client is None:
        raise Exception("Redis client not available")
    return redis_client


class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def create_tables():
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    @staticmethod
    def drop_tables():
        """Drop all database tables (use with caution!)"""
        try:
            Base.metadata.drop_all(bind=engine)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise
    
    @staticmethod
    def reset_database():
        """Reset database by dropping and recreating tables"""
        DatabaseManager.drop_tables()
        DatabaseManager.create_tables()
        logger.info("Database reset completed")


class CacheManager:
    """Redis cache management utilities"""
    
    @staticmethod
    def set_cache(key: str, value: str, ttl: int = None) -> bool:
        """Set cache value with optional TTL"""
        try:
            if redis_client:
                ttl = ttl or settings.REDIS_CACHE_TTL
                return redis_client.setex(key, ttl, value)
            return False
        except Exception as e:
            logger.error(f"Failed to set cache for key {key}: {e}")
            return False
    
    @staticmethod
    def get_cache(key: str) -> str:
        """Get cache value"""
        try:
            if redis_client:
                return redis_client.get(key)
            return None
        except Exception as e:
            logger.error(f"Failed to get cache for key {key}: {e}")
            return None
    
    @staticmethod
    def delete_cache(key: str) -> bool:
        """Delete cache key"""
        try:
            if redis_client:
                return bool(redis_client.delete(key))
            return False
        except Exception as e:
            logger.error(f"Failed to delete cache for key {key}: {e}")
            return False
    
    @staticmethod
    def clear_cache_pattern(pattern: str) -> int:
        """Clear cache keys matching pattern"""
        try:
            if redis_client:
                keys = redis_client.keys(pattern)
                if keys:
                    return redis_client.delete(*keys)
                return 0
            return 0
        except Exception as e:
            logger.error(f"Failed to clear cache pattern {pattern}: {e}")
            return 0
