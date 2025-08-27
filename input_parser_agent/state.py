"""
State objects for the Input Parser Agent LangGraph workflow
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class InputParserState:
    """
    Shared state that flows through the Input Parser Agent pipeline
    """
    # Input data (following specification)
    raw_input: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict] = None  # previous_queries, preferred_tables
    
    # Processing stages
    cleaned_input: Optional[str] = None
    is_valid: bool = False
    confidence_score: float = 0.0
    detected_intent: Optional[str] = None
    primary_table: Optional[str] = None
    columns: Optional[List[str]] = None
    mapped_fields: Optional[Dict[str, str]] = None
    schema_context: Optional[Dict] = None
    
    # Internal processing (not in final output)
    validation_result: Optional[Dict] = None
    validation_score: float = 0.0  # Internal, maps to confidence_score
    relevant_schemas: Optional[List] = None
    contextual_data: Optional[Dict] = None
    
    # Output and control
    success: bool = False
    final_output: Optional[Dict] = None
    error_info: Optional[Dict] = None
    processing_metadata: Optional[Dict] = None
    
    # Timestamps
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize start time"""
        if self.start_time is None:
            self.start_time = datetime.now()
    
    def set_error(self, error_type: str, error_message: str, details: Dict = None):
        """Helper to set error state"""
        self.success = False
        self.error_info = {
            'error_type': error_type,
            'error_message': error_message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
    
    def set_success(self, output: Dict = None):
        """Helper to set success state"""
        self.success = True
        self.final_output = output
        self.end_time = datetime.now()
        
    def get_processing_time(self) -> Optional[float]:
        """Get total processing time in milliseconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None
