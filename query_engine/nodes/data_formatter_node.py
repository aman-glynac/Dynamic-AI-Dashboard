"""
Data Formatter Node
Formats raw query results into clean data structures for visualization
"""

import logging
from ..state import QueryEngineState
from ..tools.data_formatter import DataFormatter

logger = logging.getLogger(__name__)

formatter = DataFormatter()

def data_formatter_node(state: QueryEngineState) -> QueryEngineState:
    """Format data for visualization agent"""
    logger.info("Formatting data...")
    
    # Use cached data if available, otherwise format raw data
    if state.get("cache_hit") and state.get("formatted_data"):
        data = state["formatted_data"]
    elif state.get("raw_data"):
        data = formatter.format_data(state["raw_data"])
    else:
        # Fallback data for errors
        if state.get("dimension"):
            data = [{state["dimension"]: "No data", state["metric"]: 0}]
        else:
            data = [{"value": 0, "note": "No data available"}]
    
    state["formatted_data"] = data
    
    # Build comprehensive metadata
    import time
    state["metadata"] = {
        "total_records": state.get("record_count", len(data)),
        "execution_time": f"{state.get('execution_time', 0)*1000:.1f}ms",
        "cache_hit": state.get("cache_hit", False),
        "data_source": "sales_database",
        "query": state.get("sql_query", ""),
        "intent_type": state["intent_type"],
        "chart_type": state["chart_type"],
        "metric": state["metric"],
        "dimension": state.get("dimension"),
        "has_data": len(data) > 0,
        "nodes_executed": state["nodes_executed"],
        "warnings": state.get("warnings", []),
        "processing_time": f"{(time.time() - state['processing_start_time'])*1000:.1f}ms"
    }
    
    if state.get("error"):
        state["metadata"]["error"] = state["error"]
        state["metadata"]["status"] = "error"
    else:
        state["metadata"]["status"] = "success"
    
    state["nodes_executed"].append("data_formatter")
    logger.info(f"Data formatted: {len(data)} records")
    
    return state