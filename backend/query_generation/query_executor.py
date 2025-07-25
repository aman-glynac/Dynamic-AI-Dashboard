import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd

from database import DatabaseManager
from .sql_generator import SQLGenerator, SQLGenerationResult

@dataclass
class QueryExecutionResult:
    """Structure for query execution results"""
    data: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    execution_time: float
    query_used: str
    success: bool
    error_message: Optional[str] = None

class QueryExecutor:
    """Execute SQL queries with automatic error handling and retry logic"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
        self.sql_generator = SQLGenerator()
        self.max_retry_attempts = 3
    
    def execute_sql_generation(self, enhanced_prompt: str, schema_context: str) -> Tuple[SQLGenerationResult, List[QueryExecutionResult]]:
        """
        Complete pipeline: Generate SQL -> Execute -> Return results
        
        Args:
            enhanced_prompt: Enhanced prompt with context
            schema_context: Database schema information
            
        Returns:
            Tuple of (SQL generation result, Query execution results)
        """
        
        # Generate SQL queries
        sql_result = self.sql_generator.generate_sql_from_prompt(enhanced_prompt, schema_context)
        
        if not sql_result.success:
            return sql_result, []
        
        # Execute all generated queries
        execution_results = []
        
        for i, query in enumerate(sql_result.queries):
            print(f"Executing query {i+1}/{len(sql_result.queries)}...")
            print(f"Query: {query[:100]}...")
            
            result = self._execute_single_query(query, schema_context)
            execution_results.append(result)
            
            if result.success:
                print(f"✅ Query {i+1} executed successfully: {result.row_count} rows returned")
            else:
                print(f"❌ Query {i+1} failed: {result.error_message}")
        
        return sql_result, execution_results
    
    def _execute_single_query(self, query: str, schema_context: str) -> QueryExecutionResult:
        """
        Execute a single SQL query with retry logic
        
        Args:
            query: SQL query to execute
            schema_context: Database schema for error fixing
            
        Returns:
            QueryExecutionResult
        """
        import time
        
        current_query = query
        
        for attempt in range(self.max_retry_attempts):
            try:
                start_time = time.time()
                
                # Execute query
                with sqlite3.connect(self.db_manager.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    cursor.execute(current_query)
                    rows = cursor.fetchall()
                    
                    # Convert to list of dictionaries
                    data = [dict(row) for row in rows]
                    columns = list(rows[0].keys()) if rows else []
                    
                    execution_time = time.time() - start_time
                    
                    return QueryExecutionResult(
                        data=data,
                        columns=columns,
                        row_count=len(data),
                        execution_time=execution_time,
                        query_used=current_query,
                        success=True
                    )
                    
            except sqlite3.Error as e:
                error_message = str(e)
                print(f"Attempt {attempt + 1} failed: {error_message}")
                
                if attempt < self.max_retry_attempts - 1:
                    # Try to fix the query
                    fixed_query = self.sql_generator.fix_sql_query(
                        current_query, 
                        error_message, 
                        schema_context
                    )
                    
                    if fixed_query and fixed_query != current_query:
                        print(f"Attempting fix: {fixed_query[:100]}...")
                        current_query = fixed_query
                        continue
                    else:
                        print("Could not generate a fix, retrying original query...")
                
                # If this is the last attempt or no fix available
                if attempt == self.max_retry_attempts - 1:
                    return QueryExecutionResult(
                        data=[],
                        columns=[],
                        row_count=0,
                        execution_time=0.0,
                        query_used=current_query,
                        success=False,
                        error_message=error_message
                    )
            
            except Exception as e:
                # Non-SQL errors (shouldn't happen in normal operation)
                return QueryExecutionResult(
                    data=[],
                    columns=[],
                    row_count=0,
                    execution_time=0.0,
                    query_used=current_query,
                    success=False,
                    error_message=f"Execution error: {str(e)}"
                )
        
        # This shouldn't be reached, but just in case
        return QueryExecutionResult(
            data=[],
            columns=[],
            row_count=0,
            execution_time=0.0,
            query_used=current_query,
            success=False,
            error_message="Maximum retry attempts exceeded"
        )
    
    def execute_raw_query(self, query: str) -> QueryExecutionResult:
        """
        Execute a raw SQL query (for testing/debugging)
        
        Args:
            query: Raw SQL query
            
        Returns:
            QueryExecutionResult
        """
        
        # Validate query first
        if not self.sql_generator._validate_sql_query(query):
            return QueryExecutionResult(
                data=[],
                columns=[],
                row_count=0,
                execution_time=0.0,
                query_used=query,
                success=False,
                error_message="Query failed validation (unsafe or invalid syntax)"
            )
        
        return self._execute_single_query(query, "")
    
    def get_sample_queries(self) -> List[Dict[str, str]]:
        """
        Get sample queries for testing
        
        Returns:
            List of sample queries with descriptions
        """
        
        # Get available tables
        tables = self.db_manager.get_all_tables()
        
        if not tables:
            return []
        
        sample_queries = []
        
        for table in tables[:2]:  # First 2 tables
            table_name = table['table_name']
            columns = table['columns']
            
            # Basic queries
            sample_queries.extend([
                {
                    'description': f'Show all data from {table_name}',
                    'query': f'SELECT * FROM {table_name} LIMIT 10'
                },
                {
                    'description': f'Count records in {table_name}',
                    'query': f'SELECT COUNT(*) as total_records FROM {table_name}'
                }
            ])
            
            # Column-specific queries
            if len(columns) > 1:
                sample_queries.append({
                    'description': f'Group by first column in {table_name}',
                    'query': f'SELECT {columns[0]}, COUNT(*) as count FROM {table_name} GROUP BY {columns[0]} ORDER BY count DESC LIMIT 10'
                })
        
        return sample_queries
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about query execution"""
        
        tables = self.db_manager.get_all_tables()
        
        return {
            'available_tables': len(tables),
            'table_details': [
                {
                    'name': table['table_name'],
                    'rows': table['row_count'],
                    'columns': table['column_count']
                }
                for table in tables
            ],
            'database_path': self.db_manager.db_path,
            'max_retry_attempts': self.max_retry_attempts
        }