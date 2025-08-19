"""
Input Validator Node for LangGraph workflow
"""

from typing import Dict
from datetime import datetime
import sys
import os

# Add tools to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.input_validator import InputValidator
from state import InputParserState


class InputValidatorNode:
    """LangGraph node that validates user input"""
    
    def __init__(self):
        self.input_validator = InputValidator()
    
    def __call__(self, state: InputParserState) -> InputParserState:
        """Process the input validation step"""
        try:
            print(f"✅ Input Validator: Validating '{state.cleaned_input}'")
            
            # Validate the cleaned input
            result = self.input_validator.validate(state.cleaned_input)
            
            # Update state
            state.is_valid = result.is_valid
            state.validation_score = result.confidence_score
            
            # Add processing metadata
            if not state.processing_metadata:
                state.processing_metadata = {}
            state.processing_metadata['input_validator'] = {
                'validation_score': result.confidence_score,
                'validation_details': result.validation_details,
                'processing_time_ms': result.processing_time_ms,
                'detected_intents': [intent.value for intent in result.detected_intents],
                'primary_intent': result.primary_intent.value,
                'data_elements': result.data_elements
            }
            
            if state.is_valid:
                print(f"   ✅ Valid input (score: {state.validation_score:.2f})")
            else:
                print(f"   ❌ Invalid input (score: {state.validation_score:.2f})")
                # Set error if validation failed
                state.set_error("validation_error", f"Input validation failed: {result.validation_details}")
            
            return state
            
        except Exception as e:
            state.set_error("validation_error", f"Failed to validate input: {str(e)}")
            return state


# Node function for LangGraph
def input_validator_node(state: InputParserState) -> InputParserState:
    """LangGraph node function"""
    node = InputValidatorNode()
    return node(state)
