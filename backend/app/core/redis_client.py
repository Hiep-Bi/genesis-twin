"""Redis client for caching and pub/sub"""
import json
import redis
from typing import Optional, Any, List
import logging
from datetime import timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client wrapper for caching and pub/sub operations"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub = None
    
    def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30,
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            self.redis_client.close()
            logger.info("Disconnected from Redis")
    
    # Cache operations
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL"""
        try:
            serialized = json.dumps(value)
            if ttl:
                return self.redis_client.setex(key, ttl, serialized)
            else:
                return self.redis_client.set(key, serialized)
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Error checking key {key}: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        try:
            return bool(self.redis_client.expire(key, seconds))
        except Exception as e:
            logger.error(f"Error setting expiration on {key}: {e}")
            return False
    
    def get_many(self, keys: List[str]) -> List[Optional[Any]]:
        """Get multiple values"""
        try:
            values = self.redis_client.mget(keys)
            return [json.loads(v) if v else None for v in values]
        except Exception as e:
            logger.error(f"Error getting multiple keys: {e}")
            return [None] * len(keys)
    
    def set_many(self, mapping: dict, ttl: Optional[int] = None) -> bool:
        """Set multiple key-value pairs"""
        try:
            pipeline = self.redis_client.pipeline()
            for key, value in mapping.items():
                serialized = json.dumps(value)
                if ttl:
                    pipeline.setex(key, ttl, serialized)
                else:
                    pipeline.set(key, serialized)
            pipeline.execute()
            return True
        except Exception as e:
            logger.error(f"Error setting multiple keys: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error deleting pattern {pattern}: {e}")
            return 0
    
    # Pub/Sub operations
    def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel"""
        try:
            serialized = json.dumps(message)
            return self.redis_client.publish(channel, serialized)
        except Exception as e:
            logger.error(f"Error publishing to {channel}: {e}")
            return 0
    
    def subscribe(self, *channels: str):
        """Subscribe to channels"""
        try:
            if not self.pubsub:
                self.pubsub = self.redis_client.pubsub()
            self.pubsub.subscribe(*channels)
            return self.pubsub
        except Exception as e:
            logger.error(f"Error subscribing to channels: {e}")
            return None
    
    def unsubscribe(self, *channels: str):
        """Unsubscribe from channels"""
        try:
            if self.pubsub:
                self.pubsub.unsubscribe(*channels)
        except Exception as e:
            logger.error(f"Error unsubscribing from channels: {e}")
    
    # List operations (for queues)
    def push(self, key: str, *values: Any) -> int:
        """Push values to list (right push)"""
        try:
            serialized = [json.dumps(v) for v in values]
            return self.redis_client.rpush(key, *serialized)
        except Exception as e:
            logger.error(f"Error pushing to {key}: {e}")
            return 0
    
    def pop(self, key: str, timeout: int = 0) -> Optional[Any]:
        """Pop value from list (blocking left pop)"""
        try:
            if timeout > 0:
                result = self.redis_client.blpop(key, timeout=timeout)
                if result:
                    return json.loads(result[1])
            else:
                result = self.redis_client.lpop(key)
                if result:
                    return json.loads(result)
            return None
        except Exception as e:
            logger.error(f"Error popping from {key}: {e}")
            return None
    
    def list_length(self, key: str) -> int:
        """Get list length"""
        try:
            return self.redis_client.llen(key)
        except Exception as e:
            logger.error(f"Error getting length of {key}: {e}")
            return 0
    
    # Hash operations
    def hset(self, name: str, mapping: dict) -> int:
        """Set hash fields"""
        try:
            serialized = {k: json.dumps(v) for k, v in mapping.items()}
            return self.redis_client.hset(name, mapping=serialized)
        except Exception as e:
            logger.error(f"Error setting hash {name}: {e}")
            return 0
    
    def hget(self, name: str, key: str) -> Optional[Any]:
        """Get hash field value"""
        try:
            value = self.redis_client.hget(name, key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting hash field {name}:{key}: {e}")
            return None
    
    def hgetall(self, name: str) -> dict:
        """Get all hash fields"""
        try:
            data = self.redis_client.hgetall(name)
            return {k: json.loads(v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Error getting hash {name}: {e}")
            return {}
    
    # Utility methods
    def flush_db(self):
        """Flush all keys (USE WITH CAUTION)"""
        try:
            self.redis_client.flushdb()
            logger.warning("Redis database flushed")
        except Exception as e:
            logger.error(f"Error flushing database: {e}")
    
    def ping(self) -> bool:
        """Check if Redis is responsive"""
        try:
            return self.redis_client.ping()
        except Exception:
            return False


# Global Redis client instance
redis_client = RedisClient()

