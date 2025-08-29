"""
rca_engine.py - Root Cause Analysis Engine
"""
from typing import Dict, Any
from ..types import ErrorType, Severity, ErrorHandlerState


class RCAEngine:
    """Root Cause Analysis Engine"""
    
    def analyze(self, state: ErrorHandlerState) -> Dict[str, Any]:
        """
        Analyze error to determine root cause
        
        Args:
            state: Error handler state
            
        Returns:
            Analysis results with root cause and metadata
        """
        error_type = state["error_type"]
        error_data = state["raw_error"].get("data", {})
        
        root_causes = {
            ErrorType.INPUT_ERROR: self._analyze_input_error,
            ErrorType.SCHEMA_ERROR: self._analyze_schema_error,
            ErrorType.QUERY_ERROR: self._analyze_query_error,
            ErrorType.CHART_ERROR: self._analyze_chart_error,
            ErrorType.SYSTEM_ERROR: self._analyze_system_error,
            ErrorType.VALIDATION_ERROR: self._analyze_validation_error,
        }
        
        analyzer = root_causes.get(error_type, self._default_analysis)
        return analyzer(error_data)
    
    def _analyze_input_error(self, data: Dict) -> Dict[str, Any]:
        """Analyze input errors"""
        context = data.get("context", {})
        missing = context.get("missing_params", [])
        return {
            "root_cause": "User input lacks required specificity",
            "details": f"Missing parameters: {', '.join(missing) if missing else 'unknown'}",
            "severity": Severity.LOW,
            "needs_clarification": True
        }
    
    def _analyze_schema_error(self, data: Dict) -> Dict[str, Any]:
        """Analyze schema-related errors"""
        context = data.get("context", {})
        field = context.get("field", "unknown")
        available = context.get("available_fields", [])
        return {
            "root_cause": f"Field '{field}' not found in schema",
            "details": f"Available fields: {', '.join(available[:5]) if available else 'none'}",
            "severity": Severity.MEDIUM,
            "needs_synonym_check": True,
            "available_fields": available
        }
    
    def _analyze_query_error(self, data: Dict) -> Dict[str, Any]:
        """Analyze query execution errors"""
        msg = data.get("message", "").lower()
        context = data.get("context", {})
        
        if "timeout" in msg:
            return {
                "root_cause": "Query execution timeout - dataset too large",
                "details": f"Query ran for {context.get('query_time', 'unknown')} seconds",
                "severity": Severity.MEDIUM,
                "needs_cache_check": True,
                "can_retry": True
            }
        elif "connection" in msg:
            return {
                "root_cause": "Database connection lost",
                "details": "Transient network issue",
                "severity": Severity.HIGH,
                "can_retry": True
            }
        return {
            "root_cause": "Query execution failed",
            "details": msg,
            "severity": Severity.HIGH,
            "can_retry": False
        }
    
    def _analyze_chart_error(self, data: Dict) -> Dict[str, Any]:
        """Analyze chart/visualization errors"""
        context = data.get("context", {})
        chart = context.get("chart", "unknown")
        dimension = context.get("dimension", "unknown")
        return {
            "root_cause": f"Chart type '{chart}' incompatible with '{dimension}' dimension",
            "details": f"Chart: {chart}, Data dimension: {dimension}",
            "severity": Severity.LOW,
            "needs_alternative": True
        }
    
    def _analyze_system_error(self, data: Dict) -> Dict[str, Any]:
        """Analyze system-level errors"""
        return {
            "root_cause": "System or service unavailable",
            "details": data.get("message", "Unknown system error"),
            "severity": Severity.CRITICAL,
            "needs_escalation": True
        }
    
    def _analyze_validation_error(self, data: Dict) -> Dict[str, Any]:
        """Analyze validation errors"""
        return {
            "root_cause": "Data validation failed",
            "details": data.get("message", "Validation constraints not met"),
            "severity": Severity.MEDIUM,
            "needs_format_help": True
        }
    
    def _default_analysis(self, data: Dict) -> Dict[str, Any]:
        """Default analysis for unknown error types"""
        return {
            "root_cause": "Unknown error occurred",
            "details": data.get("message", ""),
            "severity": Severity.MEDIUM
        }