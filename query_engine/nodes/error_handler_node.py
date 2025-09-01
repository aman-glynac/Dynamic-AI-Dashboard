"""
Error Handler Node
Handles query errors and provides fallback data for failed queries
"""

import logging
from ..state import QueryEngineState

logger = logging.getLogger(__name__)

def error_handler_node(state: QueryEngineState) -> QueryEngineState:
    """Handle query errors with fallback data"""
    error_msg = state.get("error", "Unknown error")
    logger.warning(f"Handling error: {error_msg}")
    
    # Provide appropriate fallback data based on intent
    if state["intent_type"] == "summary" and not state.get("dimension"):
        fallback_data = [{"value": 0, "note": "Data unavailable"}]
    elif state.get("dimension"):
        fallback_data = [{state["dimension"]: "Error", state["metric"]: 0}]
    else:
        fallback_data = [{"error": True, "message": "Query failed"}]
    
    # Update state with fallback data
    state["raw_data"] = fallback_data
    state["record_count"] = len(fallback_data)
    state["execution_time"] = 0.0
    state["nodes_executed"].append("error_handler")
    
    logger.info("Fallback data provided")
    return state