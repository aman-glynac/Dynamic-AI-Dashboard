"""
Input Parser Agent - Main LangGraph Workflow
Orchestrates the complete input parsing pipeline using LangGraph nodes
"""

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from state import InputParserState

# Try to import checkpoint functionality
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    HAS_CHECKPOINT = True
except ImportError:
    HAS_CHECKPOINT = False
    print("⚠️  Checkpoint functionality not available")
from nodes import (
    text_cleaner_node,
    input_validator_node,
    schema_retriever_node,
    field_mapper_node,
    context_injector_node
)


class InputParserAgent:
    """
    Main Input Parser Agent using LangGraph workflow
    
    Pipeline Flow:
    1. Text Cleaner: Clean raw user input
    2. Input Validator: Validate cleaned input
    3. Schema Retriever: Find relevant schemas
    4. Field Mapper: Map input to schema fields
    5. Context Injector: Add AI-enhanced context
    """
    
    def __init__(self, checkpoint_db_path: str = "agent_checkpoints.db"):
        """Initialize the agent with LangGraph workflow"""
        
        # Create the workflow graph
        self.workflow = StateGraph(InputParserState)
        
        # Add nodes to the workflow
        self.workflow.add_node("text_cleaner", text_cleaner_node)
        self.workflow.add_node("input_validator", input_validator_node)
        self.workflow.add_node("schema_retriever", schema_retriever_node)
        self.workflow.add_node("field_mapper", field_mapper_node)
        self.workflow.add_node("context_injector", context_injector_node)
        
        # Define the workflow edges
        self._setup_workflow_edges()
        
        # Set entry point
        self.workflow.set_entry_point("text_cleaner")
        
        # Add checkpointing for persistence (if available)
        if HAS_CHECKPOINT:
            memory = SqliteSaver.from_conn_string(checkpoint_db_path)
            self.app = self.workflow.compile(checkpointer=memory)
        else:
            self.app = self.workflow.compile()
    
    def _setup_workflow_edges(self):
        """Setup conditional edges for the workflow"""
        
        # Text Cleaner -> Input Validator (always)
        self.workflow.add_edge("text_cleaner", "input_validator")
        
        # Input Validator -> Schema Retriever OR END (based on validation)
        self.workflow.add_conditional_edges(
            "input_validator",
            self._should_continue_after_validation,
            {
                "continue": "schema_retriever",
                "end": END
            }
        )
        
        # Schema Retriever -> Field Mapper (always)
        self.workflow.add_edge("schema_retriever", "field_mapper")
        
        # Field Mapper -> Context Injector (always)
        self.workflow.add_edge("field_mapper", "context_injector")
        
        # Context Injector -> END (always)
        self.workflow.add_edge("context_injector", END)
    
    def _should_continue_after_validation(self, state: InputParserState) -> Literal["continue", "end"]:
        """Decide whether to continue after validation"""
        if state.error_info:
            print(f"❌ Stopping pipeline due to error: {state.error_info}")
            return "end"
        
        if not state.is_valid:
            print(f"❌ Stopping pipeline - input validation failed")
            return "end"
        
        print(f"✅ Validation passed - continuing pipeline")
        return "continue"
    
    async def process_async(self, user_input: str, thread_id: str = "default") -> InputParserState:
        """
        Process user input asynchronously through the complete pipeline
        
        Args:
            user_input: Raw user input to process
            thread_id: Unique thread ID for conversation persistence
            
        Returns:
            InputParserState: Final state with processed results
        """
        print(f"\n🚀 Starting Input Parser Agent for: '{user_input}'")
        print("=" * 60)
        
        # Create initial state
        initial_state = InputParserState(raw_input=user_input)
        
        # Configure thread for checkpointing
        config = {"configurable": {"thread_id": thread_id}}
        
        # Run the workflow
        try:
            final_state = None
            async for state in self.app.astream(initial_state, config=config):
                # Track progress through nodes
                for node_name, node_output in state.items():
                    print(f"📍 Completed: {node_name}")
                    final_state = node_output
                    
            # If no final state, use initial state
            if final_state is None:
                final_state = initial_state
            
            print("=" * 60)
            if final_state.success:
                print(f"✅ Pipeline completed successfully!")
                print(f"⏱️  Total processing time: {final_state.get_processing_time():.2f}ms")
            else:
                print(f"❌ Pipeline failed: {final_state.error_info}")
            
            return final_state
            
        except Exception as e:
            print(f"❌ Pipeline error: {str(e)}")
            initial_state.set_error("pipeline_error", f"Workflow execution failed: {str(e)}")
            return initial_state
    
    def process_sync(self, user_input: str, thread_id: str = "default") -> InputParserState:
        """
        Process user input synchronously through the complete pipeline
        
        Args:
            user_input: Raw user input to process
            thread_id: Unique thread ID for conversation persistence
            
        Returns:
            InputParserState: Final state with processed results
        """
        print(f"\n🚀 Starting Input Parser Agent for: '{user_input}'")
        print("=" * 60)
        
        # Create initial state
        initial_state = InputParserState(raw_input=user_input)
        
        # Configure thread for checkpointing
        config = {"configurable": {"thread_id": thread_id}}
        
        # Run the workflow
        try:
            result = self.app.invoke(initial_state, config=config)
            
            # Convert dict result back to InputParserState if needed
            if isinstance(result, dict):
                final_state = InputParserState(**{k: v for k, v in result.items() if k in InputParserState.__annotations__})
            else:
                final_state = result
            
            print("=" * 60)
            if final_state.success:
                print(f"✅ Pipeline completed successfully!")
                if hasattr(final_state, 'get_processing_time'):
                    print(f"⏱️  Total processing time: {final_state.get_processing_time():.2f}ms")
            else:
                if final_state.error_info:
                    print(f"❌ Pipeline failed: {final_state.error_info}")
                else:
                    print(f"❌ Pipeline failed: No error info available")
            
            return final_state
            
        except Exception as e:
            print(f"❌ Pipeline error: {str(e)}")
            initial_state.set_error("pipeline_error", f"Workflow execution failed: {str(e)}")
            return initial_state
    
    def get_workflow_state(self, thread_id: str = "default") -> Dict[str, Any]:
        """Get current workflow state for a thread"""
        config = {"configurable": {"thread_id": thread_id}}
        return self.app.get_state(config)
    
    def get_workflow_history(self, thread_id: str = "default") -> list:
        """Get workflow execution history for a thread"""
        config = {"configurable": {"thread_id": thread_id}}
        return list(self.app.get_state_history(config))


# Convenience function for quick usage
def parse_input(user_input: str) -> InputParserState:
    """
    Quick function to parse user input through the complete pipeline
    
    Args:
        user_input: Raw user input to process
        
    Returns:
        InputParserState: Final processed state
    """
    agent = InputParserAgent()
    return agent.process_sync(user_input)


def parse_input_to_dict(user_input: str, session_id: str = None, user_id: str = None, context: Dict = None) -> dict:
    """
    Parse user input and return structured result dictionary following specification
    
    Args:
        user_input: Raw user input to process
        session_id: User session identifier
        user_id: User identifier  
        context: Previous queries and preferences
        
    Returns:
        dict: Structured result matching specification output schema
    """
    result = parse_input(user_input)
    
    # Use LLM confidence if available, otherwise validation score
    confidence_score = result.confidence_score if hasattr(result, 'confidence_score') and result.confidence_score > 0 else result.validation_score
    
    return {
        "cleaned_input": result.cleaned_input or "",
        "is_valid": result.is_valid,
        "confidence_score": confidence_score,
        "detected_intent": result.detected_intent or "unknown",
        "primary_table": result.primary_table or "",
        "columns": result.columns or [],
        "mapped_fields": result.mapped_fields or {},
        "schema_context": result.schema_context or {},
        "processing_metadata": {
            "processing_time_ms": result.get_processing_time() if hasattr(result, 'get_processing_time') else 0,
            "nodes_executed": ["text_cleaner", "input_validator", "schema_retriever", "field_mapper", "context_injector"],
            "warnings": [],
            "confidence_source": "llm" if hasattr(result, 'confidence_score') and result.confidence_score > 0 else "validation"
        },
        "original_input": result.raw_input
    }


if __name__ == "__main__":
    # Example usage - prompts relevant to test database
    test_inputs = [
        "Show me total revenue by region for electronics products this month",
        "Create a bar chart comparing iPhone vs Samsung Galaxy sales performance", 
        "Display customer analytics for premium segment users aged 25-35 in North America",
        "Generate a line chart of daily revenue trends for home appliances category"
    ]
    
    agent = InputParserAgent()
    
    for i, test_input in enumerate(test_inputs):
        print(f"\n{'='*80}")
        print(f"TEST {i+1}: {test_input}")
        print(f"{'='*80}")
        
        result = agent.process_sync(test_input, thread_id=f"test_{i+1}")
        
        print(f"📊 RESULTS:")
        print(f"   Success: {result.success}")
        print(f"   Valid: {result.is_valid}")
        print(f"   Confidence Score: {result.confidence_score:.2f}")
        print(f"   Detected Intent: {result.detected_intent}")
        print(f"   Primary Table: {result.primary_table}")
        print(f"   Columns Found: {len(result.columns) if result.columns else 0}")
        print(f"   Mapped Fields: {len(result.mapped_fields) if result.mapped_fields else 0}")
        if result.error_info:
            print(f"   Error: {result.error_info}")
        
        # Specification-compliant summary
        print(f"\n🎯 SPECIFICATION OUTPUT:")
        output_dict = parse_input_to_dict(test_input)
        print(f"   cleaned_input: '{output_dict['cleaned_input']}'")
        print(f"   is_valid: {output_dict['is_valid']}")
        print(f"   confidence_score: {output_dict['confidence_score']:.2f}")
        print(f"   detected_intent: '{output_dict['detected_intent']}'")
        print(f"   primary_table: '{output_dict['primary_table']}'")
        print(f"   columns: {output_dict['columns']}")
        
        if output_dict['mapped_fields']:
            print(f"   📝 mapped_fields:")
            for field_name, field_value in output_dict['mapped_fields'].items():
                print(f"      '{field_name}': '{field_value}'")
        
        if output_dict['schema_context']:
            print(f"   📋 schema_context: {len(output_dict['schema_context'])} tables")
            for table_name in output_dict['schema_context'].keys():
                print(f"      - {table_name}")
        
        print(f"   ⏱️  processing_time_ms: {output_dict['processing_metadata']['processing_time_ms']:.1f}")
        print(f"   original_input: '{output_dict['original_input']}'")
