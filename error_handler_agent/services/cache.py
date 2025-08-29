"""
cache.py - Cache service for query results and fallback data
"""
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from ..config import CACHE_TTL

logger = logging.getLogger(__name__)


class CacheService:
    """Cache service for query results and fallback data"""
    
    def __init__(self, ttl: int = CACHE_TTL):
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.ttl = ttl
    
    def get_cached_result(self, query_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached query result if available
        
        Args:
            query_id: Query identifier
            
        Returns:
            Cached data with metadata if available, None otherwise
        """
        # Try exact match
        if query_id in self.cache:
            data, timestamp = self.cache[query_id]
            if time.time() - timestamp < self.ttl:
                logger.info(f"Cache hit for query {query_id}")
                return {
                    "data": data,
                    "cached_at": datetime.fromtimestamp(timestamp).isoformat(),
                    "age_seconds": int(time.time() - timestamp)
                }
            del self.cache[query_id]
        
        # Try to find similar recent query
        for key, (data, timestamp) in list(self.cache.items()):
            if time.time() - timestamp < self.ttl and key.startswith(query_id.split('_')[0]):
                logger.info(f"Partial cache hit for query {query_id} using {key}")
                return {
                    "data": data,
                    "cached_at": datetime.fromtimestamp(timestamp).isoformat(),
                    "age_seconds": int(time.time() - timestamp),
                    "partial_match": True
                }
        
        logger.info(f"Cache miss for query {query_id}")
        return None
    
    def store_result(self, query_id: str, data: Any):
        """
        Store query result in cache
        
        Args:
            query_id: Query identifier
            data: Data to cache
        """
        self.cache[query_id] = (data, time.time())
        logger.info(f"Cached result for query {query_id}")
    
    def clear_expired(self):
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")