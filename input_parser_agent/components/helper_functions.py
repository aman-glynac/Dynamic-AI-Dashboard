"""
Helper functions for Input Parser Agent
"""

import time
from pathlib import Path


def load_prompt_template(prompt_name: str) -> str:
    """Load prompt template from prompts folder."""
    prompts_dir = Path(__file__).parent.parent / "prompts"
    prompt_file = prompts_dir / prompt_name
    
    if prompt_file.exists():
        return prompt_file.read_text(encoding='utf-8')
    else:
        raise FileNotFoundError(f"Prompt template {prompt_name} not found")


def calculate_processing_time(start_time: float) -> float:
    """Calculate processing time in milliseconds."""
    return (time.time() - start_time) * 1000
