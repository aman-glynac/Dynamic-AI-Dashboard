"""
LangGraph nodes for Input Parser Agent
"""

from .state import InputParserState
from .tools import clean_text, validate_input, retrieve_database_schema


def clean_text_node(state: InputParserState) -> InputParserState:
    """Clean user input text."""
    raw_input = state.get("raw_input", "")
    
    clean_result = clean_text.invoke({
        "raw_input": raw_input,
        "fix_typos": True,
        "remove_noise": True
    })
    
    state["cleaned_input"] = clean_result.get("cleaned_input", raw_input)
    print(f"🧹 Cleaned: '{state['cleaned_input']}'")
    
    return state


def validate_input_node(state: InputParserState) -> InputParserState:
    """Validate cleaned input."""
    cleaned_input = state.get("cleaned_input", "")
    
    validation_result = validate_input.invoke({"cleaned_input": cleaned_input})
    
    state["is_valid"] = validation_result.get("is_valid", False)
    
    # Ensure schema_context is always initialized
    if not state["is_valid"]:
        state["schema_context"] = {}
    
    print(f"✅ Validation: {state['is_valid']}")
    
    return state


def retrieve_schemas_node(state: InputParserState) -> InputParserState:
    """Retrieve database schemas."""
    
    schema_result = retrieve_database_schema.invoke({})
    state["schema_context"] = schema_result.get('relevant_schemas', {})
    
    schemas_count = len(state["schema_context"])
    print(f"🔍 Retrieved: {schemas_count} tables (all available)")
    
    return state
