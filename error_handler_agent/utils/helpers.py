"""
helpers.py - Helper utilities for Error Handler Agent
"""
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional, List


def generate_error_id(error_data: Dict[str, Any]) -> str:
    """
    Generate unique error ID
    
    Args:
        error_data: Error payload
        
    Returns:
        Unique error identifier
    """
    timestamp = datetime.now().isoformat()
    error_hash = hashlib.md5(
        f"{timestamp}{json.dumps(error_data)}".encode()
    ).hexdigest()[:8]
    return f"err_{datetime.now().strftime('%Y%m%d')}_{error_hash}"


def extract_query_id(error_data: Dict[str, Any]) -> str:
    """
    Extract query ID from error payload
    
    Args:
        error_data: Error payload
        
    Returns:
        Query ID or 'unknown'
    """
    return error_data.get("data", {}).get("query_id", "unknown")


def format_timestamp(timestamp: Optional[str] = None) -> str:
    """
    Format timestamp to ISO format
    
    Args:
        timestamp: Optional timestamp string
        
    Returns:
        ISO formatted timestamp
    """
    if timestamp:
        try:
            # Try to parse and reformat
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.isoformat()
        except:
            pass
    return datetime.now().isoformat()


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries
    
    Args:
        base: Base dictionary
        override: Dictionary to merge into base
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def sanitize_error_message(message: str) -> str:
    """
    Sanitize error message for user display
    
    Args:
        message: Raw error message
        
    Returns:
        Sanitized message
    """
    # Remove sensitive patterns
    sensitive_patterns = [
        r'password[=:]\S+',
        r'token[=:]\S+',
        r'api[_-]?key[=:]\S+',
        r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # Credit card pattern
    ]
    
    import re
    sanitized = message
    for pattern in sensitive_patterns:
        sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
    
    return sanitized


def parse_action_string(action: str) -> tuple[str, Optional[str]]:
    """
    Parse action string into action type and parameter
    
    Args:
        action: Action string (e.g., "retry:3")
        
    Returns:
        Tuple of (action_type, parameter)
    """
    if ':' in action:
        parts = action.split(':', 1)
        return parts[0], parts[1]
    return action, None


def calculate_backoff_delay(retry_count: int, base_delay: int = 1) -> int:
    """
    Calculate exponential backoff delay
    
    Args:
        retry_count: Number of retries attempted
        base_delay: Base delay in seconds
        
    Returns:
        Delay in seconds
    """
    return min(base_delay * (2 ** retry_count), 60)  # Cap at 60 seconds


def is_transient_error(error_message: str) -> bool:
    """
    Check if error is likely transient
    
    Args:
        error_message: Error message
        
    Returns:
        True if error is likely transient
    """
    transient_keywords = [
        'timeout', 'connection', 'network', 'temporary',
        'unavailable', 'retry', 'transient', 'rate limit'
    ]
    message_lower = error_message.lower()
    return any(keyword in message_lower for keyword in transient_keywords)