import groq
import re
from typing import Dict, Any, List, Optional, Tuple
import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class SQLGenerationResult:
    """Structure for SQL generation results"""
    queries: List[str]
    processing_steps: List[Dict[str, Any]]
    chart_config: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class SQLGenerator:
    """Generate and validate SQL queries from enhanced prompts"""
    
    def __init__(self):
        self.client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
        
        # SQL validation patterns
        self.dangerous_patterns = [
            r'\bDROP\b', r'\bDELETE\b', r'\bTRUNCATE\b', r'\bALTER\b',
            r'\bINSERT\b', r'\bUPDATE\b', r'\bCREATE\b', r'\bEXEC\b'
        ]
    
    def generate_sql_from_prompt(self, enhanced_prompt: str, schema_context: str) -> SQLGenerationResult:
        """
        Generate SQL queries and processing steps from enhanced prompt
        
        Args:
            enhanced_prompt: Enhanced prompt with context
            schema_context: Database schema information
            
        Returns:
            SQLGenerationResult with queries and processing steps
        """
        
        generation_prompt = f"""
You are an expert SQL developer. Based on the enhanced prompt and schema, generate:

ENHANCED PROMPT:
{enhanced_prompt}

DATABASE SCHEMA:
{schema_context}

Generate a JSON response with this exact structure:
{{
    "queries": [
        "-- SQL query 1",
        "-- SQL query 2 (if needed)"
    ],
    "processing_steps": [
        {{
            "step": 1,
            "description": "Description of data processing step",
            "type": "aggregation|filtering|transformation|sorting",
            "details": "Specific details about the processing"
        }}
    ],
    "chart_config": {{
        "chart_type": "bar|line|pie|scatter|table",
        "x_axis": "column_name_for_x_axis",
        "y_axis": "column_name_for_y_axis",
        "title": "Chart title",
        "color_scheme": "suggested_color_scheme"
    }}
}}

REQUIREMENTS:
1. Use ONLY SELECT statements - no INSERT, UPDATE, DELETE, DROP, CREATE
2. Use exact table and column names from the schema
3. Write SQLite-compatible syntax
4. Include only queries that directly answer the user's request
5. Add processing steps for any data transformations needed
6. Suggest appropriate chart configuration

Return ONLY the JSON object, no additional text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": generation_prompt}],
                temperature=0.2,
                max_tokens=1500
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_data = self._extract_json_from_response(response_text)
            
            if not json_data:
                return SQLGenerationResult(
                    queries=[],
                    processing_steps=[],
                    chart_config={},
                    success=False,
                    error_message="Failed to parse JSON response from LLM"
                )
            
            # Validate queries
            queries = json_data.get('queries', [])
            validated_queries = []
            
            for query in queries:
                if self._validate_sql_query(query):
                    validated_queries.append(query.strip())
                else:
                    print(f"Invalid or unsafe query rejected: {query[:100]}...")
            
            if not validated_queries:
                return SQLGenerationResult(
                    queries=[],
                    processing_steps=[],
                    chart_config={},
                    success=False,
                    error_message="No valid queries generated"
                )
            
            return SQLGenerationResult(
                queries=validated_queries,
                processing_steps=json_data.get('processing_steps', []),
                chart_config=json_data.get('chart_config', {}),
                success=True
            )
            
        except Exception as e:
            return SQLGenerationResult(
                queries=[],
                processing_steps=[],
                chart_config={},
                success=False,
                error_message=f"Error generating SQL: {str(e)}"
            )
    
    def fix_sql_query(self, failed_query: str, error_message: str, schema_context: str) -> Optional[str]:
        """
        Attempt to fix a failed SQL query
        
        Args:
            failed_query: The SQL query that failed
            error_message: Error message from database
            schema_context: Database schema information
            
        Returns:
            Fixed query or None if unable to fix
        """
        
        fix_prompt = f"""
Fix this SQL query that failed:

FAILED QUERY:
{failed_query}

ERROR MESSAGE:
{error_message}

DATABASE SCHEMA:
{schema_context}

REQUIREMENTS:
1. Fix the syntax or logical error
2. Use exact table and column names from schema
3. Maintain the original intent of the query
4. Use SQLite-compatible syntax
5. Return ONLY the fixed SQL query, no explanations

Fixed Query:
"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": fix_prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            fixed_query = response.choices[0].message.content.strip()
            
            # Clean up response (remove markdown formatting if present)
            if fixed_query.startswith('```'):
                fixed_query = re.sub(r'```[\w]*\n?', '', fixed_query).strip()
            
            # Validate the fixed query
            if self._validate_sql_query(fixed_query):
                return fixed_query
            else:
                return None
                
        except Exception as e:
            print(f"Error fixing SQL query: {e}")
            return None
    
    def _extract_json_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from LLM response"""
        import json
        
        try:
            # Remove code block formatting if present
            cleaned_text = response_text
            
            # Handle various markdown code block formats
            if '```json' in cleaned_text:
                # Extract content between ```json and ```
                start_marker = '```json'
                end_marker = '```'
                start_idx = cleaned_text.find(start_marker)
                if start_idx != -1:
                    start_idx += len(start_marker)
                    end_idx = cleaned_text.find(end_marker, start_idx)
                    if end_idx != -1:
                        cleaned_text = cleaned_text[start_idx:end_idx].strip()
            
            elif cleaned_text.startswith('```'):
                # Remove generic code blocks
                cleaned_text = re.sub(r'```[\w]*\n?', '', cleaned_text).strip()
                cleaned_text = cleaned_text.replace('```', '').strip()
            
            # Find JSON object boundaries
            start_idx = cleaned_text.find('{')
            end_idx = cleaned_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = cleaned_text[start_idx:end_idx]
                
                # Clean up control characters that break JSON parsing
                # Replace problematic characters in SQL strings
                json_str = self._clean_json_string(json_str)
                
                return json.loads(json_str)
            else:
                # Try to parse the entire cleaned response as JSON
                cleaned_text = self._clean_json_string(cleaned_text)
                return json.loads(cleaned_text)
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text}")
            
            # Try aggressive cleaning as fallback
            try:
                cleaned_json = self._aggressive_json_cleanup(response_text)
                if cleaned_json:
                    return json.loads(cleaned_json)
            except:
                pass
                
            return None
    
    def _clean_json_string(self, json_str: str) -> str:
        """Clean JSON string by handling control characters in SQL queries"""
        import re
        
        # Find all string values that contain SQL queries (likely contain newlines)
        def clean_sql_in_quotes(match):
            sql_content = match.group(1)
            # Replace newlines and tabs with spaces
            sql_content = re.sub(r'\s+', ' ', sql_content)
            # Remove extra whitespace
            sql_content = sql_content.strip()
            return f'"{sql_content}"'
        
        # Pattern to match quoted strings that look like SQL
        sql_pattern = r'"([^"]*(?:SELECT|FROM|WHERE|GROUP BY|ORDER BY)[^"]*)"'
        json_str = re.sub(sql_pattern, clean_sql_in_quotes, json_str, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean other control characters
        json_str = json_str.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # Remove excessive whitespace
        json_str = re.sub(r'\s+', ' ', json_str)
        
        return json_str.strip()
    
    def _aggressive_json_cleanup(self, response_text: str) -> Optional[str]:
        """Aggressive JSON cleanup as last resort"""
        try:
            # Remove everything before first { and after last }
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx <= start_idx:
                return None
            
            json_candidate = response_text[start_idx:end_idx]
            
            # Replace all control characters with spaces
            json_candidate = re.sub(r'[\n\r\t\f\v]', ' ', json_candidate)
            
            # Fix common JSON formatting issues
            json_candidate = re.sub(r',\s*}', '}', json_candidate)  # Remove trailing commas
            json_candidate = re.sub(r',\s*]', ']', json_candidate)  # Remove trailing commas in arrays
            json_candidate = re.sub(r'\s+', ' ', json_candidate)    # Normalize whitespace
            
            return json_candidate.strip()
            
        except Exception as e:
            print(f"Aggressive cleanup failed: {e}")
            return None
    
    def _validate_sql_query(self, query: str) -> bool:
        """Validate SQL query for safety and basic syntax"""
        
        if not query or not query.strip():
            return False
        
        query_upper = query.upper()
        
        # Check for dangerous operations
        for pattern in self.dangerous_patterns:
            if re.search(pattern, query_upper):
                print(f"Rejected query with dangerous pattern: {pattern}")
                return False
        
        # Must be a SELECT statement
        if not query_upper.strip().startswith('SELECT'):
            print("Rejected non-SELECT query")
            return False
        
        # Basic syntax check - must contain FROM
        if 'FROM' not in query_upper:
            print("Rejected query without FROM clause")
            return False
        
        # Check for balanced parentheses
        if query.count('(') != query.count(')'):
            print("Rejected query with unbalanced parentheses")
            return False
        
        return True
    
    def get_query_explanation(self, query: str) -> str:
        """Generate human-readable explanation of what the query does"""
        
        explain_prompt = f"""
Explain this SQL query in simple, business-friendly language:

QUERY:
{query}

Provide a 1-2 sentence explanation of:
1. What data it retrieves
2. How it processes/groups the data
3. What insights it provides

Keep it non-technical and focused on business value.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": explain_prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Query analysis: {query[:100]}..."