"""
analysis.py - Root cause analysis node
"""
import logging
from ..types import ErrorHandlerState
from ..tools.rca_engine import RCAEngine

logger = logging.getLogger(__name__)

# Global RCA instance
rca_engine = RCAEngine()


def analyze_error(state: ErrorHandlerState) -> ErrorHandlerState:
    """Perform root cause analysis"""
    if state.get("should_skip_recovery"):
        return state
    
    analysis = rca_engine.analyze(state)
    
    state["root_cause"] = analysis["root_cause"]
    state["severity"] = analysis["severity"]
    state["needs_synonym_check"] = analysis.get("needs_synonym_check", False)
    state["needs_cache_check"] = analysis.get("needs_cache_check", False)
    
    logger.info(f"RCA: {analysis['root_cause']} - Severity: {analysis['severity']}")
    return state