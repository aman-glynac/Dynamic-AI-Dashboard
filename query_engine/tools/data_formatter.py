"""
Data Formatter Tool
Cleans and formats query results for visualization
"""

from typing import List, Dict, Any, Tuple

class DataFormatter:
    """Tool for formatting and validating query results"""
    
    @staticmethod
    def format_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean and format data for visualization
        
        Args:
            data: Raw query results
            
        Returns:
            Formatted data with proper types and null handling
        """
        formatted = []
        
        for row in data:
            clean_row = {}
            for key, value in row.items():
                # Handle null values
                if value is None:
                    if key in ['revenue', 'sales', 'profit', 'quantity', 'orders', 'value']:
                        clean_row[key] = 0
                    else:
                        clean_row[key] = ""
                # Convert string numbers to proper types
                elif isinstance(value, str) and value.replace('.', '').replace('-', '').replace('+', '').isdigit():
                    try:
                        clean_row[key] = float(value) if '.' in value else int(value)
                    except ValueError:
                        clean_row[key] = value
                else:
                    clean_row[key] = value
            
            formatted.append(clean_row)
        
        return formatted
    
    @staticmethod
    def validate_results(data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate query results for common issues
        
        Args:
            data: Query results to validate
            
        Returns:
            Tuple of (is_valid, warnings)
        """
        warnings = []
        
        if not data:
            warnings.append("No data returned from query")
            return False, warnings
        
        if len(data) > 1000:
            warnings.append(f"Large result set ({len(data)} records) - consider adding filters")
        
        # Check for null values in numeric fields
        numeric_nulls = 0
        for row in data:
            for key, value in row.items():
                if value is None and key not in ['dimension', 'category']:
                    numeric_nulls += 1
        
        if numeric_nulls > 0:
            warnings.append(f"Found {numeric_nulls} null values in numeric fields")
        
        return True, warnings