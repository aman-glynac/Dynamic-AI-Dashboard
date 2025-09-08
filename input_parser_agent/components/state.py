"""
State schema for Input Parser Agent
"""

from typing import Dict, List, Optional, Any, TypedDict


class InputParserState(TypedDict):
    """Input Parser Agent state schema."""
    
    raw_input: str
    cleaned_input: Optional[str]
    is_valid: Optional[bool]
    schema_context: Optional[Dict[str, Any]]
