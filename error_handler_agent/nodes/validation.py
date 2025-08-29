"""
validation.py - Validation and ingress node functions
"""
import json
import hashlib
import logging
from datetime import datetime
from typing import Optional
from ..types import ErrorHandlerState, ErrorType, Severity
from ..services.validator import InputValidator
from ..services.idempotency import IdempotencyChecker

logger = logging.getLogger(__name__)

# Global service instances
input_validator = InputValidator()
idempotency_checker = IdempotencyChecker()


def validate_input(state: ErrorHandlerState) -> ErrorHandlerState:
    """Validate incoming error payload"""
    is_valid, errors = input_validator.validate(state["raw_error"])
    
    state["is_valid"] = is_valid
    state["validation_errors"] = errors
    
    if not is_valid:
        logger.error(f"Invalid input: {errors}")
        state["error_type"] = ErrorType.VALIDATION_ERROR
        state["root_cause"] = f"Invalid error payload: {'; '.join(errors)}"
        state["severity"] = Severity.HIGH
        state["should_skip_recovery"] = True
    
    return state


def check_idempotency(state: ErrorHandlerState) -> ErrorHandlerState:
    """Check if this error was recently processed"""
    if not state["is_valid"]:
        return state
    
    data = state["raw_error"].get("data", {})
    query_id = data.get("query_id", "unknown")
    error_code = data.get("error_code", "unknown")
    
    cached_result = idempotency_checker.check_duplicate(query_id, error_code)
    
    if cached_result:
        # Reuse previous result
        state["telemetry_data"] = cached_result
        state["should_skip_recovery"] = True
        logger.info(f"Reusing cached result for {query_id}/{error_code}")
    
    return state


def error_ingress(state: ErrorHandlerState) -> ErrorHandlerState:
    """Receive and normalize error input"""
    if state.get("should_skip_recovery"):
        return state
    
    raw_error = state["raw_error"]
    
    # Generate unique error ID
    timestamp = datetime.now().isoformat()
    error_hash = hashlib.md5(f"{timestamp}{json.dumps(raw_error)}".encode()).hexdigest()[:8]
    error_id = f"err_{datetime.now().strftime('%Y%m%d')}_{error_hash}"
    
    # Extract basic info
    state["error_id"] = error_id
    state["error_source"] = raw_error.get("agent_id", "unknown")
    state["timestamp"] = raw_error.get("timestamp", timestamp)
    state["query_id"] = raw_error.get("data", {}).get("query_id", "unknown")
    state["retry_count"] = state.get("retry_count", 0)
    
    logger.info(f"Error ingress: {error_id} from {state['error_source']}")
    return state