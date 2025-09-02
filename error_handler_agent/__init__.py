"""
Package initialization files for Error Handler Agent
"""

# error_handler/__init__.py
ERROR_HANDLER_INIT = '''
"""
Error Handler Agent Package
"""
from .main import ErrorHandlerAgent, create_error_handler
from .types import ErrorType, Severity, NextAction, ErrorHandlerState

__version__ = "1.0.0"
__all__ = [
    "ErrorHandlerAgent",
    "create_error_handler",
    "ErrorType",
    "Severity",
    "NextAction",
    "ErrorHandlerState"
]
'''

# error_handler/nodes/__init__.py
NODES_INIT = '''
"""
LangGraph nodes for Error Handler Agent
"""
from .validation import validate_input, check_idempotency, error_ingress
from .classification import classify_error
from .analysis import analyze_error
from .recovery import determine_recovery, execute_automated_actions
from .messaging import generate_message
from .telemetry import format_feedback, emit_telemetry

__all__ = [
    "validate_input",
    "check_idempotency",
    "error_ingress",
    "classify_error",
    "analyze_error",
    "determine_recovery",
    "execute_automated_actions",
    "generate_message",
    "format_feedback",
    "emit_telemetry"
]
'''

# error_handler/services/__init__.py
SERVICES_INIT = '''
"""
Core services for Error Handler Agent
"""
from .cache import CacheService
from .idempotency import IdempotencyChecker
from .validator import InputValidator
from .synonym_mapper import SynonymMapper
from .router import FeedbackRouter

__all__ = [
    "CacheService",
    "IdempotencyChecker",
    "InputValidator",
    "SynonymMapper",
    "FeedbackRouter"
]
'''

# error_handler/tools/__init__.py
TOOLS_INIT = '''
"""
Analysis and recovery tools for Error Handler Agent
"""
from .classifier import ErrorClassifierTool
from .rca_engine import RCAEngine
from .recovery_policy import RecoveryPolicyEngine
from .message_generator import MessageGenerator

__all__ = [
    "ErrorClassifierTool",
    "RCAEngine",
    "RecoveryPolicyEngine",
    "MessageGenerator"
]
'''

# error_handler/utils/__init__.py
UTILS_INIT = '''
"""
Utility functions for Error Handler Agent
"""
from .logging import setup_logging, get_logger
from .helpers import (
    generate_error_id,
    extract_query_id,
    format_timestamp,
    truncate_text,
    merge_dicts,
    sanitize_error_message,
    parse_action_string,
    calculate_backoff_delay,
    is_transient_error
)

__all__ = [
    "setup_logging",
    "get_logger",
    "generate_error_id",
    "extract_query_id",
    "format_timestamp",
    "truncate_text",
    "merge_dicts",
    "sanitize_error_message",
    "parse_action_string",
    "calculate_backoff_delay",
    "is_transient_error"
]
'''

# error_handler/examples/__init__.py
EXAMPLES_INIT = '''
"""
Example scripts for Error Handler Agent
"""
'''