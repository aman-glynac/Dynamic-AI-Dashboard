"""
State definitions for Query Engine Agent workflow
Defines the TypedDict state that flows through all LangGraph nodes
"""

from typing import Dict, List, Any, Optional
from typing_extensions import TypedDict

class QueryEngineState(TypedDict):
    """
    State object that flows through the Query Engine Agent workflow
    Contains all data needed for processing natural language queries into formatted results
    """
    
    # Input from Intent Resolver Agent
    intent_type: str                    # Type of query: summary, comparison, trend
    metric: str                         # What to measure: revenue, sales, orders, etc.
    dimension: Optional[str]            # How to group: month, region, category, etc.
    chart_type: str                     # Visualization type: bar, line, pie, card
    schema_validated: bool              # Whether schema validation passed
    context_merged: bool                # Whether context was merged from previous queries
    raw_prompt: str                     # Original user prompt
    enhanced_prompt: str                # Processed prompt with context
    
    # Processing state
    cache_key: str                      # Generated cache key for this query
    cache_hit: bool                     # Whether result was found in cache
    sql_query: str                      # Generated SQL query
    execution_time: float               # Database execution time in seconds
    query_success: bool                 # Whether query executed successfully
    
    # Data state
    raw_data: List[Dict[str, Any]]      # Raw results from database
    record_count: int                   # Number of records returned
    
    # Output state
    formatted_data: List[Dict[str, Any]] # Cleaned and formatted data for visualization
    metadata: Dict[str, Any]            # Metadata about the query and results
    
    # Error handling
    error: Optional[str]                # Error message if something failed
    warnings: List[str]                 # Non-fatal warnings during processing
    
    # Workflow tracking
    nodes_executed: List[str]           # List of nodes that have been executed
    processing_start_time: float        # When processing started (for timing)

class QueryEngineInput(TypedDict):
    """Input format from Intent Resolver Agent"""
    intent_type: str
    metric: str
    dimension: Optional[str]
    chart_type: str
    schema_validated: bool
    context_merged: bool
    raw_prompt: str
    enhanced_prompt: str

class QueryEngineOutput(TypedDict):
    """Output format for Visualization Agent"""
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]