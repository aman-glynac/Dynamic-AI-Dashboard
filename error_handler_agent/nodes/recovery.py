"""
recovery.py - Recovery strategy and execution nodes
"""
import logging
from ..types import ErrorHandlerState
from ..tools.recovery_policy import RecoveryPolicyEngine
from ..services.cache import CacheService
from ..tools.synonym_mapper import SynonymMapper

logger = logging.getLogger(__name__)

# Global service instances
cache_service = CacheService()
synonym_mapper = SynonymMapper()
policy_engine = RecoveryPolicyEngine(cache_service, synonym_mapper)


def determine_recovery(state: ErrorHandlerState) -> ErrorHandlerState:
    """Determine recovery strategy"""
    if state.get("should_skip_recovery"):
        return state
    
    analysis = {
        "needs_synonym_check": state.get("needs_synonym_check", False),
        "needs_cache_check": state.get("needs_cache_check", False),
        "can_retry": True
    }
    
    strategy = policy_engine.determine_strategy(state, analysis)
    
    state["recovery_strategy"] = strategy.strategy
    state["automated_actions"] = strategy.actions
    state["recovery_suggestions"] = strategy.suggestions
    state["next_action"] = strategy.next_action
    state["cached_data"] = strategy.cached_data
    state["field_mapping"] = strategy.field_mapping
    
    logger.info(f"Recovery strategy: {strategy.strategy}")
    return state


def execute_automated_actions(state: ErrorHandlerState) -> ErrorHandlerState:
    """Execute automated recovery actions"""
    if state.get("should_skip_recovery"):
        return state
    
    actions = state.get("automated_actions", [])
    for action in actions:
        if action.startswith("retry:"):
            count = int(action.split(":")[1])
            state["retry_count"] = count
            logger.info(f"Scheduling retry {count}")
        elif action.startswith("map:"):
            logger.info(f"Applied synonym mapping: {action}")
        elif action == "use_cache:true" and state.get("cached_data"):
            logger.info("Using cached results for recovery")
        elif action.startswith("escalate:"):
            logger.warning(f"Escalating issue: {action}")
    
    state["context_preserved"] = True
    return state