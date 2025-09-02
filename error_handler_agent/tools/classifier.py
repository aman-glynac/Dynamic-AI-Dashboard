"""
classifier.py - Error classification tool
"""
import logging
from collections import defaultdict
from typing import Dict, Tuple
from ..types import ErrorType
from ..config import ERROR_PATTERNS

logger = logging.getLogger(__name__)


class ErrorClassifierTool:
    """Classifies raw errors into canonical types"""
    
    def __init__(self):
        self.error_patterns = ERROR_PATTERNS
    
    def classify(self, error_data: Dict) -> Tuple[ErrorType, float]:
        """
        Classify error and return type with confidence
        
        Args:
            error_data: Raw error data
            
        Returns:
            Tuple of (ErrorType, confidence_score)
        """
        error_msg = error_data.get("data", {}).get("message", "").lower()
        error_code = error_data.get("data", {}).get("error_code", "").lower()
        
        # Check explicit error_type first
        if "error_type" in error_data.get("data", {}):
            explicit_type = error_data["data"]["error_type"]
            if explicit_type in [e.value for e in ErrorType]:
                return ErrorType(explicit_type), 0.95
        
        # Pattern matching with scoring
        scores = defaultdict(float)
        for error_type_str, patterns in self.error_patterns.items():
            error_type = ErrorType(error_type_str)
            for pattern in patterns:
                if pattern in error_msg:
                    scores[error_type] += 0.6
                if pattern in error_code:
                    scores[error_type] += 0.4
        
        if scores:
            best_match = max(scores.items(), key=lambda x: x[1])
            confidence = min(best_match[1], 0.95)
            logger.debug(f"Classified error as {best_match[0]} with confidence {confidence}")
            return best_match[0], confidence
        
        # Default to validation error if unknown
        logger.warning(f"Could not classify error, defaulting to VALIDATION_ERROR")
        return ErrorType.VALIDATION_ERROR, 0.5