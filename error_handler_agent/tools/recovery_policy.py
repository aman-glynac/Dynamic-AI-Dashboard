"""
recovery_policy.py - Recovery policy engine
"""
import logging
from typing import Dict, Any
from ..types import ErrorType, ErrorHandlerState, NextAction, RecoveryStrategy
from ..config import MAX_RETRIES, RETRY_DELAYS, CHART_COMPATIBILITY

logger = logging.getLogger(__name__)


class RecoveryPolicyEngine:
    """Decides and orchestrates recovery strategies"""
    
    def __init__(self, cache_service=None, synonym_mapper=None):
        self.max_retries = MAX_RETRIES
        self.retry_delays = RETRY_DELAYS
        self.cache = cache_service
        self.synonyms = synonym_mapper
    
    def determine_strategy(self, state: ErrorHandlerState, analysis: Dict) -> RecoveryStrategy:
        """
        Determine recovery strategy based on error type and analysis
        
        Args:
            state: Current error handler state
            analysis: Root cause analysis results
            
        Returns:
            Recovery strategy with actions and suggestions
        """
        error_type = state["error_type"]
        severity = state["severity"]
        retry_count = state.get("retry_count", 0)
        
        strategies = {
            ErrorType.INPUT_ERROR: self._input_error_strategy,
            ErrorType.SCHEMA_ERROR: self._schema_error_strategy,
            ErrorType.QUERY_ERROR: self._query_error_strategy,
            ErrorType.CHART_ERROR: self._chart_error_strategy,
            ErrorType.SYSTEM_ERROR: self._system_error_strategy,
            ErrorType.VALIDATION_ERROR: self._validation_error_strategy,
        }
        
        strategy_func = strategies.get(error_type, self._default_strategy)
        strategy_dict = strategy_func(state, analysis)
        
        # Convert to RecoveryStrategy object
        return RecoveryStrategy(
            strategy=strategy_dict["strategy"],
            actions=strategy_dict["actions"],
            suggestions=strategy_dict["suggestions"],
            next_action=strategy_dict["next_action"],
            needs_cache=strategy_dict.get("needs_cache", False),
            needs_synonyms=strategy_dict.get("needs_synonyms", False),
            cached_data=strategy_dict.get("cached_data"),
            field_mapping=strategy_dict.get("field_mapping")
        )
    
    def _input_error_strategy(self, state: ErrorHandlerState, analysis: Dict) -> Dict[str, Any]:
        """Strategy for input errors"""
        context = state["raw_error"].get("data", {}).get("context", {})
        missing = context.get("missing_params", ["time range", "metric"])
        
        return {
            "strategy": "clarify",
            "actions": ["generate_clarifying_prompts"],
            "suggestions": [
                f"Please specify the {param}" for param in missing[:2]
            ] + ["Try: 'show revenue by month for last quarter'"],
            "next_action": NextAction.AWAIT_USER,
            "needs_cache": False,
            "needs_synonyms": False
        }
    
    def _schema_error_strategy(self, state: ErrorHandlerState, analysis: Dict) -> Dict[str, Any]:
        """Strategy for schema errors"""
        context = state["raw_error"].get("data", {}).get("context", {})
        missing_field = context.get("field", "")
        available = context.get("available_fields", [])
        
        # Try synonym mapping first
        if available and missing_field and self.synonyms:
            mapping = self.synonyms.find_mapping(missing_field, available)
            if mapping:
                return {
                    "strategy": "auto_remap_field",
                    "actions": ["apply_field_mapping", f"map:{missing_field}->{mapping[missing_field]}"],
                    "field_mapping": mapping,
                    "suggestions": [f"Using '{mapping[missing_field]}' instead of '{missing_field}'"],
                    "next_action": NextAction.RESUME,
                    "needs_cache": False,
                    "needs_synonyms": False
                }
        
        # Fall back to suggestions
        return {
            "strategy": "suggest_alternatives",
            "actions": ["list_available_fields"],
            "suggestions": [
                f"Available fields: {', '.join(available[:5])}",
                "Check field names for typos",
                "Use 'show schema' to see all fields"
            ] if available else ["Schema information unavailable"],
            "next_action": NextAction.AWAIT_USER if available else NextAction.ESCALATE,
            "needs_cache": False,
            "needs_synonyms": True
        }
    
    def _query_error_strategy(self, state: ErrorHandlerState, analysis: Dict) -> Dict[str, Any]:
        """Strategy for query errors"""
        retry_count = state.get("retry_count", 0)
        query_id = state["query_id"]
        can_retry = analysis.get("can_retry", True)
        
        # Check cache first
        if self.cache:
            cached = self.cache.get_cached_result(query_id)
            if cached:
                return {
                    "strategy": "use_cached_data",
                    "actions": ["use_cache:true", f"cache_age:{cached['age_seconds']}s"],
                    "cached_data": cached,
                    "suggestions": [
                        f"Using cached results from {cached['age_seconds']} seconds ago",
                        "Fresh data temporarily unavailable"
                    ],
                    "next_action": NextAction.RESUME,
                    "needs_cache": False,
                    "needs_synonyms": False
                }
        
        # Try retry if allowed
        if can_retry and retry_count < self.max_retries:
            return {
                "strategy": "retry_with_backoff",
                "actions": [
                    f"retry:{retry_count+1}",
                    f"backoff:{self.retry_delays[retry_count]}s",
                    "reduce_scope"
                ],
                "suggestions": [
                    "Retrying with optimized query",
                    "Consider reducing date range",
                    f"Attempt {retry_count+1} of {self.max_retries}"
                ],
                "next_action": NextAction.RESUME,
                "needs_cache": True,
                "needs_synonyms": False
            }
        
        # Escalate if no other options
        return {
            "strategy": "escalate_query_issue",
            "actions": ["escalate:ops", "log_query_failure"],
            "suggestions": [
                "Query cannot be completed at this time",
                "Try a simpler query or smaller date range",
                "Technical team has been notified"
            ],
            "next_action": NextAction.ESCALATE,
            "needs_cache": True,
            "needs_synonyms": False
        }
    
    def _chart_error_strategy(self, state: ErrorHandlerState, analysis: Dict) -> Dict[str, Any]:
        """Strategy for chart errors"""
        context = state["raw_error"].get("data", {}).get("context", {})
        chart_type = context.get("chart", "unknown")
        dimension = context.get("dimension", "")
        
        # Check compatibility matrix
        key = (chart_type.lower(), dimension.lower())
        alternatives = CHART_COMPATIBILITY.get(key, ["bar", "line", "table"])
        
        return {
            "strategy": "suggest_chart_alternatives",
            "actions": [f"suggest_chart:{alternatives[0]}"],
            "suggestions": [
                f"'{chart_type}' doesn't work with {dimension} data",
                f"Try: {', '.join(alternatives)} chart instead",
                "Or change the grouping dimension"
            ],
            "next_action": NextAction.AWAIT_USER,
            "needs_cache": False,
            "needs_synonyms": False
        }
    
    def _system_error_strategy(self, state: ErrorHandlerState, analysis: Dict) -> Dict[str, Any]:
        """Strategy for system errors"""
        # Check for cached data as fallback
        cached = None
        if self.cache:
            cached = self.cache.get_cached_result(state["query_id"])
        
        actions = ["escalate:critical", "notify_ops"]
        suggestions = ["System temporarily unavailable"]
        
        if cached:
            actions.append("provide_cached_fallback")
            suggestions.append(f"Showing last known results from {cached['age_seconds']}s ago")
        
        suggestions.append("Please try again in 15 minutes")
        
        return {
            "strategy": "system_failure_handling",
            "actions": actions,
            "cached_data": cached,
            "suggestions": suggestions,
            "next_action": NextAction.ESCALATE,
            "needs_cache": True,
            "needs_synonyms": False
        }
    
    def _validation_error_strategy(self, state: ErrorHandlerState, analysis: Dict) -> Dict[str, Any]:
        """Strategy for validation errors"""
        return {
            "strategy": "provide_validation_help",
            "actions": ["show_format_examples", "list_constraints"],
            "suggestions": [
                "Check data format requirements",
                "Example: dates should be YYYY-MM-DD",
                "Ensure all required fields are provided"
            ],
            "next_action": NextAction.AWAIT_USER,
            "needs_cache": False,
            "needs_synonyms": False
        }
    
    def _default_strategy(self, state: ErrorHandlerState, analysis: Dict) -> Dict[str, Any]:
        """Default strategy for unknown errors"""
        return {
            "strategy": "generic_recovery",
            "actions": ["log_unknown_error", "preserve_context"],
            "suggestions": [
                "An unexpected error occurred",
                "Please try rephrasing your request",
                "Contact support with error ID: " + state.get("error_id", "unknown")
            ],
            "next_action": NextAction.AWAIT_USER,
            "needs_cache": False,
            "needs_synonyms": False
        }