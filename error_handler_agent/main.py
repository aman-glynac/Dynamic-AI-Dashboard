"""
main.py - Main entry point and graph builder for Error Handler Agent
"""
import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END

# Import types and state
from .types import ErrorHandlerState

# Import node functions
from .nodes.validation import validate_input, check_idempotency, error_ingress
from .nodes.classification import classify_error
from .nodes.analysis import analyze_error
from .nodes.recovery import determine_recovery, execute_automated_actions
from .nodes.messaging import generate_message
from .nodes.telemetry import format_feedback, emit_telemetry

# Import services
from .services.cache import CacheService
from .tools.synonym_mapper import SynonymMapper
from .services.router import FeedbackRouter
from .services.idempotency import IdempotencyChecker
from .services.validator import InputValidator

# Configure logging
from .utils.logging import setup_logging

logger = logging.getLogger(__name__)


class ErrorHandlerAgent:
    """Main Error Handler Agent class"""
    
    def __init__(self):
        """Initialize the Error Handler Agent"""
        # Setup logging
        setup_logging()
        
        # Initialize services
        self.cache_service = CacheService()
        self.synonym_mapper = SynonymMapper()
        self.idempotency_checker = IdempotencyChecker()
        self.input_validator = InputValidator()
        self.feedback_router = FeedbackRouter()
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info("Error Handler Agent initialized")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for Error Handler Agent"""
        workflow = StateGraph(ErrorHandlerState)
        
        # Add nodes
        workflow.add_node("validate_input", validate_input)
        workflow.add_node("check_idempotency", check_idempotency)
        workflow.add_node("error_ingress", error_ingress)
        workflow.add_node("classify_error", classify_error)
        workflow.add_node("analyze_error", analyze_error)
        workflow.add_node("determine_recovery", determine_recovery)
        workflow.add_node("execute_actions", execute_automated_actions)
        workflow.add_node("generate_message", generate_message)
        workflow.add_node("format_feedback", format_feedback)
        workflow.add_node("emit_telemetry", emit_telemetry)
        
        # Define edges
        workflow.add_edge("validate_input", "check_idempotency")
        workflow.add_edge("check_idempotency", "error_ingress")
        workflow.add_edge("error_ingress", "classify_error")
        workflow.add_edge("classify_error", "analyze_error")
        workflow.add_edge("analyze_error", "determine_recovery")
        workflow.add_edge("determine_recovery", "execute_actions")
        workflow.add_edge("execute_actions", "generate_message")
        workflow.add_edge("generate_message", "format_feedback")
        workflow.add_edge("format_feedback", "emit_telemetry")
        workflow.add_edge("emit_telemetry", END)
        
        # Set entry point
        workflow.set_entry_point("validate_input")
        
        return workflow.compile()
    
    def handle_error(self, error_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an error from the pipeline
        
        Args:
            error_payload: Standardized error payload
            
        Returns:
            Feedback object with recovery instructions
        """
        # Initialize state
        initial_state = self._create_initial_state(error_payload)
        
        # Run through the graph
        result = self.graph.invoke(initial_state)
        
        # Return telemetry data as feedback
        return result.get("telemetry_data", {})
    
    def _create_initial_state(self, error_payload: Dict[str, Any]) -> ErrorHandlerState:
        """Create initial state from error payload"""
        return ErrorHandlerState(
            raw_error=error_payload,
            is_valid=True,
            validation_errors=[],
            error_id="",
            error_type=None,
            error_source="",
            timestamp="",
            query_id="",
            root_cause=None,
            confidence=0.0,
            severity=None,
            recovery_strategy=None,
            automated_actions=[],
            retry_count=0,
            cached_data=None,
            field_mapping=None,
            user_message=None,
            recovery_suggestions=[],
            next_action=None,
            context_preserved=False,
            session_context={},
            telemetry_data={},
            should_skip_recovery=False,
            needs_synonym_check=False,
            needs_cache_check=False
        )
    
    def register_feedback_handlers(self, ui_callback=None, pipeline_callback=None, ops_callback=None):
        """
        Register callbacks for feedback routing
        
        Args:
            ui_callback: Function to send feedback to UI
            pipeline_callback: Function to send feedback to pipeline
            ops_callback: Function to send feedback to operations
        """
        if ui_callback:
            self.feedback_router.register_ui(ui_callback)
        if pipeline_callback:
            self.feedback_router.register_pipeline(pipeline_callback)
        if ops_callback:
            self.feedback_router.register_ops(ops_callback)


def create_error_handler() -> ErrorHandlerAgent:
    """Factory function to create Error Handler Agent instance"""
    return ErrorHandlerAgent()


# Example usage
if __name__ == "__main__":
    from datetime import datetime
    
    # Create agent
    agent = create_error_handler()
    
    # Register simple feedback handlers
    agent.register_feedback_handlers(
        ui_callback=lambda fb: print(f"[UI] {fb.get('user_message', 'No message')}"),
        pipeline_callback=lambda fb: print(f"[PIPELINE] Action: {fb.get('action', 'none')}"),
        ops_callback=lambda fb: print(f"[OPS] Error {fb.get('error_id', 'unknown')}")
    )
    
    # Test error
    test_error = {
        "agent_id": "query_engine",
        "timestamp": datetime.now().isoformat(),
        "status": "error",
        "data": {
            "error_type": "schema_error",
            "error_code": "FIELD_NOT_FOUND",
            "message": "Field 'revenue' not found in schema",
            "context": {
                "field": "revenue",
                "available_fields": ["sales", "product_name", "sku", "date", "region"]
            },
            "query_id": "q_test_001"
        }
    }
    
    # Handle error
    result = agent.handle_error(test_error)
    print(f"\nResult: {result}")