# Type definitions and enums
"""
types.py - Type definitions and enums for Error Handler Agent
"""
from enum import Enum
from typing import Dict, List, Optional, Any, TypedDict
from dataclasses import dataclass


class ErrorType(str, Enum):
    """Canonical error types"""
    INPUT_ERROR = "input_error"
    SCHEMA_ERROR = "schema_error"
    QUERY_ERROR = "query_error"
    CHART_ERROR = "chart_error"
    SYSTEM_ERROR = "system_error"
    VALIDATION_ERROR = "validation_error"


class Severity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NextAction(str, Enum):
    """Next action for pipeline"""
    RESUME = "resume"
    AWAIT_USER = "await_user"
    ESCALATE = "escalate"


class ErrorHandlerState(TypedDict):
    """Main state container for Error Handler Agent"""
    # Input
    raw_error: Dict[str, Any]
    
    # Validation
    is_valid: bool
    validation_errors: List[str]
    
    # Error Context
    error_id: str
    error_type: Optional[ErrorType]
    error_source: str
    timestamp: str
    query_id: str
    
    # Analysis Results
    root_cause: Optional[str]
    confidence: float
    severity: Optional[Severity]
    
    # Recovery Context
    recovery_strategy: Optional[str]
    automated_actions: List[str]
    retry_count: int
    cached_data: Optional[Dict[str, Any]]
    field_mapping: Optional[Dict[str, str]]
    
    # Output
    user_message: Optional[str]
    recovery_suggestions: List[str]
    next_action: Optional[NextAction]
    context_preserved: bool
    
    # Session Context
    session_context: Dict[str, Any]
    
    # Telemetry
    telemetry_data: Dict[str, Any]
    
    # Routing
    should_skip_recovery: bool
    needs_synonym_check: bool
    needs_cache_check: bool


@dataclass
class ErrorPayload:
    """Standardized error payload structure"""
    agent_id: str
    timestamp: str
    status: str
    data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "timestamp": self.timestamp,
            "status": self.status,
            "data": self.data
        }


@dataclass
class RecoveryStrategy:
    """Recovery strategy details"""
    strategy: str
    actions: List[str]
    suggestions: List[str]
    next_action: NextAction
    needs_cache: bool = False
    needs_synonyms: bool = False
    cached_data: Optional[Dict[str, Any]] = None
    field_mapping: Optional[Dict[str, str]] = None