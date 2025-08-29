"""
validator.py - Input validation service
"""
import re
from datetime import datetime
from typing import Dict, List, Tuple
from ..config import REQUIRED_FIELDS, REQUIRED_DATA_FIELDS
from ..types import ErrorType


class InputValidator:
    """Validates incoming error payloads"""
    
    def __init__(self):
        self.required_fields = REQUIRED_FIELDS
        self.required_data_fields = REQUIRED_DATA_FIELDS
        self.valid_error_types = [e.value for e in ErrorType]
    
    def validate(self, payload: Dict) -> Tuple[bool, List[str]]:
        """
        Validate error payload structure and content
        
        Args:
            payload: Raw error payload
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check structure
        for field in self.required_fields:
            if field not in payload:
                errors.append(f"Missing required field: {field}")
        
        if "data" in payload:
            for field in self.required_data_fields:
                if field not in payload["data"]:
                    errors.append(f"Missing required data field: {field}")
            
            # Validate error_type
            if "error_type" in payload["data"]:
                if payload["data"]["error_type"] not in self.valid_error_types:
                    errors.append(f"Invalid error_type: {payload['data']['error_type']}")
            
            # Validate query_id format
            if "query_id" in payload["data"]:
                if not re.match(r'^[qQ]_\w+$', payload["data"]["query_id"]):
                    errors.append(f"Invalid query_id format: {payload['data']['query_id']}")
        
        # Validate timestamp
        if "timestamp" in payload:
            try:
                datetime.fromisoformat(payload["timestamp"].replace('Z', '+00:00'))
            except:
                errors.append(f"Invalid timestamp format: {payload['timestamp']}")
        
        return len(errors) == 0, errors