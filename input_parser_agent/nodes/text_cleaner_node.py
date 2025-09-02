"""
Text Cleaner Node for LangGraph workflow
"""

from typing import Dict
from datetime import datetime

from ..tools.text_cleaner import TextCleaner
from ..state import InputParserState


class TextCleanerNode:
    """LangGraph node that cleans raw user input"""
    
    def __init__(self):
        self.text_cleaner = TextCleaner()
    
    def __call__(self, state: InputParserState) -> InputParserState:
        """Process the text cleaning step"""
        try:
            print(f"🧹 Text Cleaner: Processing '{state.raw_input}'")
            
            # Clean the input
            result = self.text_cleaner.clean_text(state.raw_input)
            
            # Update state
            state.cleaned_input = result['cleaned_input']
            
            # Add processing metadata
            if not state.processing_metadata:
                state.processing_metadata = {}
            state.processing_metadata['text_cleaner'] = {
                'original_length': len(state.raw_input),
                'cleaned_length': len(result['cleaned_input']),
                'processing_time_ms': result.get('processing_time_ms', 0),
                'changes_made': result.get('changes_made', [])
            }
            
            print(f"   ✅ Cleaned: '{state.cleaned_input}'")
            
            return state
            
        except Exception as e:
            state.set_error("text_cleaning_error", f"Failed to clean text: {str(e)}")
            return state


# Node function for LangGraph
def text_cleaner_node(state: InputParserState) -> InputParserState:
    """LangGraph node function"""
    node = TextCleanerNode()
    return node(state)
