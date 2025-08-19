"""
Context Injector Node for LangGraph workflow
"""

from typing import Dict
from datetime import datetime
import sys
import os

# Add tools to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.context_injector import ContextInjector
from state import InputParserState


class ContextInjectorNode:
    """LangGraph node that injects contextual information"""
    
    def __init__(self):
        self.context_injector = ContextInjector()
    
    def __call__(self, state: InputParserState) -> InputParserState:
        """Process the context injection step"""
        try:
            print(f"🧠 Context Injector: Enhancing '{state.cleaned_input}' with schema context")
            
            # Inject context
            result = self.context_injector.inject_context(
                original_input=state.raw_input,
                cleaned_input=state.cleaned_input,
                validation_result=state.validation_result or {},
                field_mapping_result={'mapped_fields': state.mapped_fields or {}},
                schema_cache={'schemas': state.relevant_schemas or []},
                session_id=state.session_id
            )
            
            # Update state with specification-compliant fields
            state.contextual_data = {
                'ai_intent': result.ai_intent.__dict__ if result.ai_intent else {},
                'session_context': result.session_context.__dict__ if result.session_context else {},
                'schema_context': result.schema_context.__dict__ if result.schema_context else {}
            }
            
            # Extract detected intent and confidence from LLM
            if result.ai_intent:
                state.detected_intent = result.ai_intent.intent_type
                # Use LLM confidence score as overall confidence (much better than validation score)
                state.confidence_score = result.ai_intent.confidence
            else:
                state.detected_intent = "unknown"
                # Fallback to validation score if no LLM response
                state.confidence_score = state.validation_score
                
            # Extract primary table and columns from schemas
            if state.relevant_schemas and len(state.relevant_schemas) > 0:
                state.primary_table = state.relevant_schemas[0].get('name', '')
                # Extract columns from all relevant schemas
                all_columns = set()
                schema_context = {}
                for schema in state.relevant_schemas:
                    table_name = schema.get('name', '')
                    table_info = schema.get('schema', {})
                    if 'columns' in table_info:
                        all_columns.update(table_info['columns'].keys())
                        # Build proper schema context structure
                        schema_context[table_name] = {
                            "columns": list(table_info['columns'].keys()),
                            "relationships": [f"{k}:{v}" for k, v in table_info.get('relationships', {}).items()],
                            "data_types": {k: v.get('data_type', 'unknown') for k, v in table_info.get('columns', {}).items()}
                        }
                state.columns = list(all_columns)
                state.schema_context = schema_context
            else:
                state.primary_table = ""
                state.columns = []
                state.schema_context = {}
            
            # Add processing metadata
            if not state.processing_metadata:
                state.processing_metadata = {}
            state.processing_metadata['context_injector'] = {
                'primary_table_identified': bool(state.primary_table),
                'columns_extracted': len(state.columns),
                'schemas_processed': len(state.relevant_schemas) if state.relevant_schemas else 0,
                'intent_detected': state.detected_intent != "unknown"
            }
            
            print(f"   ✅ Detected intent: {state.detected_intent}")
            print(f"   📋 Primary table: {state.primary_table}")
            print(f"   �️ Extracted {len(state.columns)} columns")
            
            # Mark as complete
            state.set_success()
            
            return state
            
        except Exception as e:
            state.set_error("context_injection_error", f"Failed to inject context: {str(e)}")
            return state


# Node function for LangGraph
def context_injector_node(state: InputParserState) -> InputParserState:
    """LangGraph node function"""
    node = ContextInjectorNode()
    return node(state)
