"""
Schema Retriever Node for LangGraph workflow
"""

from typing import Dict, List
from datetime import datetime
import sys
import os

# Add tools to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.schema_retriever import SchemaRetriever, DatabaseConfig
from state import InputParserState


class SchemaRetrieverNode:
    """LangGraph node that retrieves relevant schemas"""
    
    def __init__(self):
        # Create a database config pointing to our test database
        default_config = DatabaseConfig(
            db_type="sqlite",
            connection_params={"database": "test_dashboard.db"},
            schema_name=None
        )
        self.schema_retriever = SchemaRetriever(default_config)
    
    def __call__(self, state: InputParserState) -> InputParserState:
        """Process the schema retrieval step"""
        try:
            print(f"📋 Schema Retriever: Finding schemas for '{state.cleaned_input}'")
            
            # Get relevant schemas
            # Extract potential table/column terms from the cleaned input
            keywords = state.cleaned_input.lower().split()
            relevant_schemas = []
            
            # Get all schemas and filter by relevance
            try:
                full_schema = self.schema_retriever.get_full_schema()
                
                # Simple keyword matching to find relevant tables
                for table_name, table_info in full_schema.items():
                    relevance_score = 0
                    
                    # Check if table name matches any keywords
                    for keyword in keywords:
                        if keyword in table_name.lower():
                            relevance_score += 0.8
                        
                        # Check column names
                        if 'columns' in table_info:
                            for col_name in table_info['columns'].keys():
                                if keyword in col_name.lower():
                                    relevance_score += 0.5
                    
                    if relevance_score > 0:
                        relevant_schemas.append({
                            'name': table_name,
                            'confidence': min(relevance_score, 1.0),
                            'schema': table_info
                        })
                
                # Sort by confidence
                relevant_schemas.sort(key=lambda x: x['confidence'], reverse=True)
                relevant_schemas = relevant_schemas[:5]  # Top 5
                
            except Exception as e:
                print(f"   ⚠️ Could not retrieve schemas: {e}")
                relevant_schemas = []
            
            # Update state
            state.relevant_schemas = relevant_schemas
            
            # Add processing metadata
            if not state.processing_metadata:
                state.processing_metadata = {}
            state.processing_metadata['schema_retriever'] = {
                'schemas_found': len(state.relevant_schemas),
                'schema_names': [schema.get('name', 'unnamed') for schema in state.relevant_schemas],
                'processing_time_ms': 0,  # Could add timing if needed
                'search_method': 'keyword_matching',
                'confidence_scores': [schema.get('confidence', 0.0) for schema in state.relevant_schemas]
            }
            
            print(f"   📋 Found {len(state.relevant_schemas)} relevant schemas")
            for schema in state.relevant_schemas:
                print(f"      - {schema.get('name', 'unnamed')} (confidence: {schema.get('confidence', 0.0):.2f})")
            
            return state
            
        except Exception as e:
            state.set_error("schema_retrieval_error", f"Failed to retrieve schemas: {str(e)}")
            return state


# Node function for LangGraph
def schema_retriever_node(state: InputParserState) -> InputParserState:
    """LangGraph node function"""
    node = SchemaRetrieverNode()
    return node(state)
