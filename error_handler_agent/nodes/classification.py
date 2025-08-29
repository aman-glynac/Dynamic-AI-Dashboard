"""
classification.py - Error classification node
"""
import logging
from ..types import ErrorHandlerState
from ..tools.classifier import ErrorClassifierTool

logger = logging.getLogger(__name__)

# Global classifier instance
classifier = ErrorClassifierTool()


def classify_error(state: ErrorHandlerState) -> ErrorHandlerState:
    """Classify error into canonical type"""
    if state.get("should_skip_recovery"):
        return state
    
    error_type, confidence = classifier.classify(state["raw_error"])
    
    state["error_type"] = error_type
    state["confidence"] = confidence
    
    logger.info(f"Classified as {error_type} with confidence {confidence}")
    return state