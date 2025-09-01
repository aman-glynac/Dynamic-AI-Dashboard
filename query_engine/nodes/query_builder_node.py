"""
Query Builder Node
Constructs SQL queries from structured intent using proper aggregation functions
"""

import logging
from ..state import QueryEngineState
from ..tools.sql_builder import SQLBuilder

logger = logging.getLogger(__name__)

# Global SQL builder instance
sql_builder = SQLBuilder()

def query_builder_node(state: QueryEngineState) -> QueryEngineState:
    """
    Build SQL query from user intent
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with generated SQL query
    """
    logger.info("Building SQL query...")
    
    try:
        # Build SQL query using the fixed aggregation logic
        query = sql_builder.build_query(
            intent_type=state["intent_type"],
            metric=state["metric"],
            dimension=state.get("dimension"),
            filters=None,  # TODO: Add filter support
            limit=50 if state["intent_type"] == "trend" else 20
        )
        
        # Update state
        state["sql_query"] = query
        state["nodes_executed"].append("query_builder")
        
        logger.info(f"Generated SQL query: {query[:100]}...")
        
    except Exception as e:
        error_msg = f"Query building failed: {str(e)}"
        state["error"] = error_msg
        logger.error(error_msg)
    
    return state