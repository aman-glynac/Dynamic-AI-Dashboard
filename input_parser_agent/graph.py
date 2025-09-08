"""
Input Parser Agent Graph
"""

from langgraph.graph import StateGraph, START, END

from .components.state import InputParserState
from .components.nodes import (
    clean_text_node, validate_input_node, retrieve_schemas_node
)


builder = StateGraph(InputParserState)

builder.add_node("clean_text", clean_text_node)
builder.add_node("validate_input", validate_input_node)
builder.add_node("retrieve_schemas", retrieve_schemas_node)

def route_after_validation(state: InputParserState) -> str:
    """Route based on validation result."""
    return "continue" if state.get("is_valid", False) else "end"

builder.add_edge(START, "clean_text")
builder.add_edge("clean_text", "validate_input")
builder.add_conditional_edges(
    "validate_input",
    route_after_validation,
    {
        "continue": "retrieve_schemas",
        "end": END
    }
)
builder.add_edge("retrieve_schemas", END)

input_parser_agent = builder.compile()
input_parser_agent.__doc__ = InputParserState.__doc__
