"""
Pydantic schemas for Input Parser Agent
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class InputValidationOutput(BaseModel):
    """Schema for input validation results."""
    is_valid: bool = Field(description="Whether the input is a valid data visualization request")
    primary_intent: str = Field(description="Basic intent classification: show_data, compare_data, trend_analysis, or invalid")
    confidence_score: float = Field(description="Validation confidence score (0.0-1.0)", ge=0.0, le=1.0)
    data_elements: Optional[List[str]] = Field(description="Basic data elements mentioned in input", default=None)
