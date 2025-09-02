"""
telemetry.py - Telemetry and feedback formatting nodes
"""
import json
import logging
from datetime import datetime
from ..types import ErrorHandlerState, NextAction
from ..services.router import FeedbackRouter
from ..services.idempotency import IdempotencyChecker

logger = logging.getLogger(__name__)

# Global service instances
feedback_router = FeedbackRouter()
idempotency_checker = IdempotencyChecker()


def format_feedback(state: ErrorHandlerState) -> ErrorHandlerState:
    """Format final feedback output"""
    feedback = {
        "error_id": state.get("error_id", "unknown"),
        "error_type": state["error_type"].value if state.get("error_type") else "unknown",
        "error_source": state.get("error_source", "unknown"),
        "severity": state["severity"].value if state.get("severity") else "medium",
        "confidence": state.get("confidence", 0.0),
        "user_message": state.get("user_message"),
        "recovery_suggestions": state.get("recovery_suggestions", []),
        "automated_actions": state.get("automated_actions", []),
        "context_preserved": state.get("context_preserved", True),
        "query_id": state.get("query_id", "unknown"),
        "timestamp": state.get("timestamp", datetime.now().isoformat()),
        "next_action": state["next_action"].value if state.get("next_action") else "await_user",
        "cached_data": state.get("cached_data"),
        "field_mapping": state.get("field_mapping")
    }
    
    state["telemetry_data"] = feedback
    
    # Store result for idempotency
    query_id = state.get("query_id", "unknown")
    error_code = state["raw_error"].get("data", {}).get("error_code", "unknown")
    idempotency_checker.store_result(query_id, error_code, feedback)
    
    logger.info(f"Formatted feedback for error {state.get('error_id')}")
    return state


def emit_telemetry(state: ErrorHandlerState) -> ErrorHandlerState:
    """Emit metrics and logs for monitoring"""
    telemetry = state.get("telemetry_data", {})
    
    # In production, send to monitoring system
    logger.info(f"Telemetry emitted: {json.dumps(telemetry, indent=2)}")
    
    # Route feedback
    next_action = state.get("next_action", NextAction.AWAIT_USER)
    feedback_router.route_feedback(telemetry, next_action)
    
    return state