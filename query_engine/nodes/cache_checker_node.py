"""
Cache Checker Node - Fixed Version
The issue is likely that cache instances aren't shared between calls
"""

import logging
from ..state import QueryEngineState
from ..tools.cache_client import CacheClient

logger = logging.getLogger(__name__)

# Create a module-level cache instance that persists between calls
_cache_client = None

def get_cache_client():
    """Get or create shared cache client instance"""
    global _cache_client
    if _cache_client is None:
        _cache_client = CacheClient()
    return _cache_client

def cache_checker_node(state: QueryEngineState) -> QueryEngineState:
    """
    Check if results are cached for this query
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with cache information
    """
    logger.info("Checking cache...")
    
    # Use shared cache instance
    cache_client = get_cache_client()
    
    # Generate cache key from query parameters
    cache_key = cache_client.generate_cache_key(
        intent_type=state["intent_type"],
        metric=state["metric"],
        dimension=state.get("dimension", ""),
        filters={}
    )
    
    # Check for cached result
    cached_result = cache_client.get(cache_key)
    
    # Update state
    state["cache_key"] = cache_key
    state["cache_hit"] = cached_result is not None
    state["nodes_executed"].append("cache_checker")
    
    if cached_result:
        logger.info(f"Cache hit for key: {cache_key}")
        # Load cached data into state
        state["formatted_data"] = cached_result["data"]
        state["metadata"] = cached_result["metadata"]
        state["metadata"]["cache_hit"] = True
    else:
        logger.info(f"Cache miss for key: {cache_key}")
    
    return state