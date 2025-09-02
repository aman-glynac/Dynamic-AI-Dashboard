"""
Configuration settings for Query Engine Agent
"""

import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class QueryEngineConfig:
    """Configuration for Query Engine Agent"""
    
    # Database settings
    database_path: str = "test_dashboard.db"
    connection_timeout: int = 30
    query_timeout: int = 60
    
    # Cache settings
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes
    max_cache_size: int = 1000
    
    # Query settings
    default_limit: int = 100
    max_limit: int = 1000
    trend_limit: int = 50
    comparison_limit: int = 20
    
    # Performance settings
    max_processing_time: int = 30  # seconds
    enable_query_optimization: bool = True
    
    # Logging settings
    log_level: str = "INFO"
    log_queries: bool = True
    log_performance: bool = True
    
    @classmethod
    def from_env(cls) -> 'QueryEngineConfig':
        """Create config from environment variables"""
        return cls(
            database_path=os.getenv("QE_DATABASE_PATH", "test_dashboard.db"),
            cache_enabled=os.getenv("QE_CACHE_ENABLED", "true").lower() == "true",
            cache_ttl_seconds=int(os.getenv("QE_CACHE_TTL", "300")),
            default_limit=int(os.getenv("QE_DEFAULT_LIMIT", "100")),
            log_level=os.getenv("QE_LOG_LEVEL", "INFO")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "database_path": self.database_path,
            "connection_timeout": self.connection_timeout,
            "query_timeout": self.query_timeout,
            "cache_enabled": self.cache_enabled,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "max_cache_size": self.max_cache_size,
            "default_limit": self.default_limit,
            "max_limit": self.max_limit,
            "trend_limit": self.trend_limit,
            "comparison_limit": self.comparison_limit,
            "max_processing_time": self.max_processing_time,
            "enable_query_optimization": self.enable_query_optimization,
            "log_level": self.log_level,
            "log_queries": self.log_queries,
            "log_performance": self.log_performance
        }