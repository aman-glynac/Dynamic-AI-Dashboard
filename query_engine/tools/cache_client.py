"""
Cache Client Tool
Manages in-memory caching of query results with TTL support
"""

import time
import hashlib
import json
from typing import Dict, Any, Optional

class CacheClient:
    """Simple in-memory cache for query results"""
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minute default TTL
        self.cache = {}
        self.ttl_seconds = ttl_seconds
        self.access_times = {}
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if not expired"""
        if key not in self.cache:
            return None
            
        # Check if expired
        access_time = self.access_times.get(key, 0)
        if time.time() - access_time > self.ttl_seconds:
            del self.cache[key]
            del self.access_times[key]
            return None
            
        return self.cache[key]
    
    def set(self, key: str, value: Dict[str, Any]):
        """Store result in cache"""
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def generate_cache_key(self, intent_type: str, metric: str, dimension: str = "", 
                          filters: Dict = None) -> str:
        """Generate cache key from query parameters"""
        key_data = f"{intent_type}_{metric}_{dimension}"
        if filters:
            key_data += f"_{json.dumps(filters, sort_keys=True)}"
        
        return hashlib.md5(key_data.encode()).hexdigest()[:12]
    
    def clear(self):
        """Clear all cached data"""
        self.cache.clear()
        self.access_times.clear()