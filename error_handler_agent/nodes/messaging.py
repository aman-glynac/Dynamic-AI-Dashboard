"""
messaging.py - Message generation node
"""
import logging
from ..types import ErrorHandlerState
from ..tools.message_generator import MessageGenerator

logger = logging.getLogger(__name__)

# Global message generator instance
msg_generator = MessageGenerator()


def generate_message(state: ErrorHandlerState) -> ErrorHandlerState:
    """Generate user-facing message"""
    if state.get("should_skip_recovery"):
        return state
    
    state["user_message"] = msg_generator.generate(state)
    
    logger.info(f"Generated message: {state['user_message']}")
    return state