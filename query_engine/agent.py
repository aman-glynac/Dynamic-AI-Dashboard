"""
Main LangGraph Query Engine Agent
Orchestrates the complete workflow from intent to formatted results
"""

import time
import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from .state import QueryEngineState, QueryEngineInput, QueryEngineOutput
from .nodes import (
    cache_checker_node,
    query_builder_node,
    query_executor_node,
    data_formatter_node,
    cache_manager_node,
    error_handler_node
)

logger = logging.getLogger(__name__)

class QueryEngineAgent:
    """LangGraph-based Query Engine Agent"""
    
    def __init__(self, db_path: str = "test_dashboard.db"):
        self.db_path = db_path
        self.graph = self._create_graph()
        logger.info(f"LangGraph Query Engine Agent initialized with database: {db_path}")
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        # Create workflow
        workflow = StateGraph(QueryEngineState)
        
        # Add nodes
        workflow.add_node("cache_checker", cache_checker_node)
        workflow.add_node("query_builder", query_builder_node)
        workflow.add_node("query_executor", query_executor_node)
        workflow.add_node("data_formatter", data_formatter_node)
        workflow.add_node("cache_manager", cache_manager_node)
        workflow.add_node("error_handler", error_handler_node)
        
        # Set entry point
        workflow.set_entry_point("cache_checker")
        
        # Define conditional edges
        workflow.add_conditional_edges(
            "cache_checker",
            self._cache_decision,
            {
                "cache_hit": "data_formatter",
                "cache_miss": "query_builder"
            }
        )
        
        workflow.add_edge("query_builder", "query_executor")
        
        workflow.add_conditional_edges(
            "query_executor", 
            self._execution_decision,
            {
                "success": "data_formatter",
                "error": "error_handler"
            }
        )
        
        workflow.add_edge("error_handler", "data_formatter")
        workflow.add_edge("data_formatter", "cache_manager")
        workflow.add_edge("cache_manager", END)
        
        return workflow.compile()
    
    def _cache_decision(self, state: QueryEngineState) -> Literal["cache_hit", "cache_miss"]:
        """Decide cache routing"""
        return "cache_hit" if state["cache_hit"] else "cache_miss"
    
    def _execution_decision(self, state: QueryEngineState) -> Literal["success", "error"]:
        """Decide execution routing"""
        return "error" if state.get("error") else "success"
    
    def process(self, intent_data: QueryEngineInput) -> QueryEngineOutput:
        """
        Process intent data through the LangGraph workflow
        
        Args:
            intent_data: Output from Intent Resolver Agent
            
        Returns:
            Dictionary with data and metadata for Visualization Agent
        """
        logger.info("Starting LangGraph Query Engine workflow...")
        
        # Initialize state
        initial_state = QueryEngineState(
            # Input from Intent Resolver
            intent_type=intent_data.get("intent_type", ""),
            metric=intent_data.get("metric", ""),
            dimension=intent_data.get("dimension"),
            chart_type=intent_data.get("chart_type", "bar"),
            schema_validated=intent_data.get("schema_validated", False),
            context_merged=intent_data.get("context_merged", False),
            raw_prompt=intent_data.get("raw_prompt", ""),
            enhanced_prompt=intent_data.get("enhanced_prompt", ""),
            
            # Initialize processing state
            cache_key="",
            cache_hit=False,
            sql_query="",
            execution_time=0.0,
            query_success=False,
            
            # Initialize data state
            raw_data=[],
            record_count=0,
            
            # Initialize output state
            formatted_data=[],
            metadata={},
            
            # Initialize error handling
            error=None,
            warnings=[],
            
            # Initialize workflow tracking
            nodes_executed=[],
            processing_start_time=time.time()
        )
        
        try:
            # Execute the LangGraph workflow
            final_state = self.graph.invoke(initial_state)
            
            logger.info("Workflow completed successfully")
            
            # Return in format expected by Visualization Agent
            return QueryEngineOutput(
                data=final_state["formatted_data"],
                metadata=final_state["metadata"]
            )
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            
            # Return error response
            return QueryEngineOutput(
                data=[{"error": True, "message": "Workflow execution failed"}],
                metadata={
                    "total_records": 0,
                    "execution_time": "0ms",
                    "cache_hit": False,
                    "data_source": "error",
                    "error": str(e),
                    "status": "error"
                }
            )