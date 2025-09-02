"""
Input Parser Agent - Main LangGraph Workflow
Orchestrates the complete input parsing pipeline using LangGraph nodes
"""

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from .state import InputParserState

# Try to import checkpoint functionality
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    HAS_CHECKPOINT = True
except ImportError:
    HAS_CHECKPOINT = False
    print("⚠️  Checkpoint functionality not available")
    
from .nodes import (
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

