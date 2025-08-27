"""
Field Mapper Node for LangGraph workflow
"""

from typing import Dict
from datetime import datetime

from ..tools.field_mapper import FieldMapper
from ..state import InputParserState


class FieldMapperNode:
    """LangGraph node that maps input to schema fields"""
    
    def __init__(self):
        # Provide a default schema cache (will be populated by schema retriever)
        default_schema_cache = {}
        self.field_mapper = FieldMapper(default_schema_cache)
    
    def __call__(self, state: InputParserState) -> InputParserState:
        """Process the field mapping step"""
        try:
            print(f"🗺️ Field Mapper: Mapping '{state.cleaned_input}' to schema fields")
            
            # Build schema cache from relevant schemas
            schema_cache = {}
            if state.relevant_schemas:
                for schema in state.relevant_schemas:
                    table_name = schema.get('name', '')
                    table_info = schema.get('schema', {})
                    if table_name and 'columns' in table_info:
                        schema_cache[table_name] = table_info
            
            # Update field mapper with actual schemas
            if schema_cache:
                self.field_mapper.schema_cache = schema_cache
                self.field_mapper.business_vocabulary = self.field_mapper._build_business_vocabulary()
            
            # Map input to schema fields
            result = self.field_mapper.map_fields(state.cleaned_input)
            
            # Convert mappings to simple dict format for output
            mapped_fields = {}
            if hasattr(result, 'mappings') and result.mappings:
                for mapping in result.mappings:
                    mapped_fields[mapping.user_term] = mapping.full_path
            
            state.mapped_fields = mapped_fields
            
            # Add processing metadata
            if not state.processing_metadata:
                state.processing_metadata = {}
            state.processing_metadata['field_mapper'] = {
                'fields_mapped': len(state.mapped_fields),
                'field_names': list(state.mapped_fields.keys()),
                'schemas_used': len(schema_cache),
                'mapping_confidence': result.confidence if hasattr(result, 'confidence') else 0.0
            }
            
            print(f"   🗺️ Mapped {len(state.mapped_fields)} fields:")
            for field_name, field_value in state.mapped_fields.items():
                print(f"      - {field_name}: {field_value}")
            
            return state
            
        except Exception as e:
            state.set_error("field_mapping_error", f"Failed to map fields: {str(e)}")
            return state


# Node function for LangGraph
def field_mapper_node(state: InputParserState) -> InputParserState:
    """LangGraph node function"""
    node = FieldMapperNode()
    return node(state)
