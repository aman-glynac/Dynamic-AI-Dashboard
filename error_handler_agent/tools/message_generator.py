"""
message_generator.py - User message generation tool
"""
import logging
from typing import Optional
from ..types import ErrorType, ErrorHandlerState
from ..config import MESSAGE_TEMPLATES

logger = logging.getLogger(__name__)


class MessageGenerator:
    """Generates user-friendly error messages"""
    
    def __init__(self):
        self.templates = MESSAGE_TEMPLATES
    
    def generate(self, state: ErrorHandlerState) -> str:
        """
        Generate concise, actionable user message
        
        Args:
            state: Error handler state with all context
            
        Returns:
            User-friendly error message
        """
        error_type = state["error_type"]
        root_cause = state.get("root_cause", "Unknown issue")
        suggestions = state.get("recovery_suggestions", [])
        
        # Check if we auto-fixed something
        if state.get("field_mapping"):
            mapping = state["field_mapping"]
            return f"I found a matching field. {suggestions[0] if suggestions else ''}"
        
        if state.get("cached_data"):
            cache_info = state["cached_data"]
            age = cache_info["age_seconds"]
            return f"Using cached results from {age} seconds ago. {suggestions[0] if suggestions else ''}"
        
        # Get appropriate template
        template = self.templates.get(
            error_type.value if error_type else "default",
            self.templates["default"]
        )
        
        suggestion_text = suggestions[0] if suggestions else "Please try again"
        
        message = template.format(
            root_cause=root_cause,
            suggestion=suggestion_text
        )
        
        logger.debug(f"Generated message: {message}")
        return message
    
    def generate_detailed(self, state: ErrorHandlerState) -> str:
        """
        Generate detailed error message with all suggestions
        
        Args:
            state: Error handler state
            
        Returns:
            Detailed error message with all recovery suggestions
        """
        base_message = self.generate(state)
        suggestions = state.get("recovery_suggestions", [])
        
        if len(suggestions) > 1:
            detailed = f"{base_message}\n\nAdditional suggestions:"
            for i, suggestion in enumerate(suggestions[1:], 1):
                detailed += f"\n{i}. {suggestion}"
            return detailed
        
        return base_message