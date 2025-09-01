"""
Database Client Tool
Handles database connections and query execution
"""

import sqlite3
import time
from typing import List, Dict, Any, Tuple

class DatabaseClient:
    """Tool for executing queries against SQLite database"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute SQL query and return results with timing
        
        Args:
            query: SQL query string
            
        Returns:
            Dictionary with success status, data, timing, and error info
        """
        start_time = time.time()
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            data = [dict(row) for row in rows]
            record_count = len(data)
            
            conn.close()
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'data': data,
                'execution_time': execution_time,
                'record_count': record_count,
                'error': None
            }
            
        except sqlite3.Error as e:
            return {
                'success': False,
                'data': [],
                'execution_time': time.time() - start_time,
                'record_count': 0,
                'error': f"SQLite error: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'data': [],
                'execution_time': time.time() - start_time,
                'record_count': 0,
                'error': f"Database error: {str(e)}"
            }
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except:
            return False