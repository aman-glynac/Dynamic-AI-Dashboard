"""
Cache Manager Node - Fixed Version
Uses the same shared cache instance as cache_checker_node
"""

import logging
from ..state import QueryEngineState

logger = logging.getLogger(__name__)

def cache_manager_node(state: QueryEngineState) -> QueryEngineState:
    """Manage caching of results"""
    logger.info("Managing cache...")
    
    # Import the shared cache function
    from .cache_checker_node import get_cache_client
    cache_client = get_cache_client()
    
    # Only cache successful results that aren't already cached
    if (state.get("query_success") and 
        not state.get("cache_hit") and 
        not state.get("error")):
        
        cache_data = {
            "data": state["formatted_data"],
            "metadata": state["metadata"].copy()
        }
        cache_data["metadata"]["cache_hit"] = True
        
        cache_client.set(state["cache_key"], cache_data)
        logger.info(f"Results cached with key: {state['cache_key']}")
    else:
        if state.get("cache_hit"):
            logger.info("Already cached, no action needed")
        elif state.get("error"):
            logger.info("Error occurred, not caching")
        else:
            logger.info("Query unsuccessful, not caching")
    
    state["nodes_executed"].append("cache_manager")
    return state