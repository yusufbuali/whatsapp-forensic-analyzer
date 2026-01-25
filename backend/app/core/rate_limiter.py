"""
Redis-based Rate Limiter for Production

Replaces in-memory rate limiter with Redis for:
- Persistence across application restarts
- Consistency across multiple instances
- Better performance at scale
"""

from typing import Tuple
from datetime import datetime, timedelta, timezone
import redis
import logging

from .config import settings

logger = logging.getLogger(__name__)


class RedisRateLimiter:
    """
    Redis-based rate limiter for production use

    Uses Redis sorted sets to track login attempts with automatic expiry
    """

    def __init__(self, redis_client: redis.Redis = None):
        """
        Initialize rate limiter with Redis connection

        Args:
            redis_client: Optional Redis client (creates new one if not provided)
        """
        if redis_client:
            self.redis = redis_client
        else:
            try:
                self.redis = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                )
                # Test connection
                self.redis.ping()
                logger.info("Redis rate limiter initialized successfully")
            except Exception as e:
                logger.warning(
                    f"Redis connection failed, falling back to in-memory: {e}"
                )
                self.redis = None

    def check_rate_limit(
        self, key: str, max_attempts: int, window_minutes: int
    ) -> Tuple[bool, int]:
        """
        Check if rate limit is exceeded

        Args:
            key: Identifier (e.g., username or IP)
            max_attempts: Maximum allowed attempts
            window_minutes: Time window in minutes

        Returns:
            (is_allowed, remaining_attempts)
        """
        if not self.redis:
            # Fallback to no rate limiting if Redis unavailable
            logger.warning("Redis unavailable, rate limiting disabled")
            return True, max_attempts

        try:
            # Redis key for this limiter
            redis_key = f"ratelimit:{key}"

            # Current timestamp
            now = datetime.now(timezone.utc)
            window_start = now - timedelta(minutes=window_minutes)

            # Remove old entries (outside time window)
            self.redis.zremrangebyscore(
                redis_key, 0, window_start.timestamp()
            )

            # Count attempts in current window
            current_attempts = self.redis.zcard(redis_key)

            if current_attempts >= max_attempts:
                # Rate limit exceeded
                return False, 0

            # Rate limit not exceeded
            remaining = max_attempts - current_attempts
            return True, remaining

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # On error, allow request (fail open for availability)
            return True, max_attempts

    def record_attempt(self, key: str, window_minutes: int = 15):
        """
        Record a failed attempt

        Args:
            key: Identifier (e.g., username or IP)
            window_minutes: Time window for expiry
        """
        if not self.redis:
            return

        try:
            redis_key = f"ratelimit:{key}"
            now = datetime.now(timezone.utc)

            # Add attempt with current timestamp as score
            self.redis.zadd(redis_key, {str(now.timestamp()): now.timestamp()})

            # Set expiry on the key (cleanup)
            self.redis.expire(redis_key, window_minutes * 60)

        except Exception as e:
            logger.error(f"Failed to record attempt: {e}")

    def reset(self, key: str):
        """
        Reset attempts for a key (e.g., after successful login)

        Args:
            key: Identifier to reset
        """
        if not self.redis:
            return

        try:
            redis_key = f"ratelimit:{key}"
            self.redis.delete(redis_key)

        except Exception as e:
            logger.error(f"Failed to reset rate limit: {e}")

    def get_remaining_time(self, key: str, window_minutes: int) -> int:
        """
        Get seconds until rate limit reset

        Args:
            key: Identifier
            window_minutes: Time window in minutes

        Returns:
            Seconds until oldest attempt expires (0 if no attempts)
        """
        if not self.redis:
            return 0

        try:
            redis_key = f"ratelimit:{key}"

            # Get oldest attempt
            oldest = self.redis.zrange(redis_key, 0, 0, withscores=True)

            if not oldest:
                return 0

            oldest_timestamp = oldest[0][1]
            oldest_time = datetime.fromtimestamp(oldest_timestamp, tz=timezone.utc)
            expires_at = oldest_time + timedelta(minutes=window_minutes)
            now = datetime.now(timezone.utc)

            if expires_at > now:
                return int((expires_at - now).total_seconds())

            return 0

        except Exception as e:
            logger.error(f"Failed to get remaining time: {e}")
            return 0


# Global rate limiter instance (production-ready with Redis)
login_rate_limiter = RedisRateLimiter()
