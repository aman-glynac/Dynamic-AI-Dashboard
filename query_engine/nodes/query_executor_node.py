"""
Query Executor Node
Executes SQL queries against the database and handles connection/execution errors
"""

import logging
from ..state import QueryEngineState
from ..tools.database_client import DatabaseClient

logger = logging.getLogger(__name__)

# Global database client instance
db_client = DatabaseClient("test_dashboard.db")

def query_executor_node(state: QueryEngineState) -> QueryEngineState:
    """
    Execute SQL query against database
    
    Args:
        state: Current workflow state with SQL query
        
    Returns:
        Updated state with query results or error
    """
    logger.info("Executing SQL query...")
    
    try:
        # Execute the query
        results = db_client.execute_query(state["sql_query"])
        
        if results["success"]:
            # Successful execution
            state["raw_data"] = results["data"]
            state["execution_time"] = results["execution_time"]
            state["record_count"] = results["record_count"]
            state["query_success"] = True
            state["nodes_executed"].append("query_executor")
            
            logger.info(f"Query executed successfully: {results['record_count']} records in {results['execution_time']*1000:.1f}ms")
        else:
            # Query execution failed
            state["error"] = results["error"]
            state["query_success"] = False
            logger.error(f"Query execution failed: {results['error']}")
            
    except Exception as e:
        # Unexpected error
        error_msg = f"Query execution error: {str(e)}"
        state["error"] = error_msg
        state["query_success"] = False
        logger.error(error_msg)
    
    return state