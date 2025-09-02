import groq
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from .db_manager import DatabaseManager

load_dotenv()

class SchemaAnalyzer:
    """Analyze database schema and generate LLM-friendly context"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.db_manager = db_manager or DatabaseManager()
    
    def analyze_complete_schema(self) -> Dict[str, Any]:
        """
        Analyze entire database schema and generate comprehensive context
        
        Returns:
            Complete schema analysis for LLM consumption
        """
        # Get all tables
        tables = self.db_manager.get_all_tables()
        
        if not tables:
            return {
                'database_summary': 'No tables found in database',
                'tables': [],
                'sql_context': 'Database is empty',
                'query_examples': []
            }
        
        # Analyze each table
        table_analyses = []
        for table_info in tables:
            table_analysis = self._analyze_single_table(table_info['table_name'])
            table_analyses.append(table_analysis)
        
        # Generate overall database context
        database_context = self._generate_database_context(tables, table_analyses)
        
        return {
            'database_summary': database_context['summary'],
            'tables': table_analyses,
            'sql_context': database_context['sql_context'],
            'query_examples': database_context['query_examples'],
            'relationships': database_context['relationships']
        }
    
    def _analyze_single_table(self, table_name: str) -> Dict[str, Any]:
        """Analyze a single table and generate context"""
        schema = self.db_manager.get_table_schema(table_name)
        
        # Generate LLM analysis of the table
        table_description = self._generate_table_description(schema)
        column_insights = self._generate_column_insights(schema)
        query_patterns = self._generate_query_patterns(schema)
        
        return {
            'table_name': table_name,
            'description': table_description,
            'columns': schema['columns'],
            'column_insights': column_insights,
            'row_count': schema['row_count'],
            'sample_data': schema['sample_data'],
            'query_patterns': query_patterns,
            'sql_examples': self._generate_sql_examples(schema)
        }
    
    def _generate_table_description(self, schema: Dict[str, Any]) -> str:
        """Generate table description using LLM"""
        columns_info = "\n".join([
            f"- {col['name']} ({col['type']}): {col['unique_count']} unique values, {col['non_null_count']} non-null"
            for col in schema['columns']
        ])
        
        sample_data_str = str(schema['sample_data'][:2])
        
        prompt = f"""
        Analyze this database table and provide a clear business description:
        
        Table: {schema['table_name']}
        Rows: {schema['row_count']}
        Columns: {schema['column_count']}
        
        Column Details:
        {columns_info}
        
        Sample Data:
        {sample_data_str}
        
        Provide a concise description (50-100 words) of:
        1. What business entity this table represents
        2. What kind of analysis it supports
        3. Key insights it could provide
        
        Focus on business value and use cases.
        """
        
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_column_insights(self, schema: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate insights for key columns"""
        insights = []
        
        for col in schema['columns']:
            # Focus on important columns (high uniqueness or key patterns)
            if col['unique_count'] > 1 or 'id' in col['name'].lower():
                prompt = f"""
                Analyze this database column:
                
                Column: {col['name']}
                Type: {col['type']}
                Unique values: {col['unique_count']}
                Non-null count: {col['non_null_count']}
                
                In 1-2 sentences, describe:
                1. What this column likely represents
                2. How it might be used in queries/analysis
                
                Be specific and practical.
                """
                
                try:
                    response = self.client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                        max_tokens=150
                    )
                    
                    insights.append({
                        'column': col['name'],
                        'insight': response.choices[0].message.content.strip()
                    })
                except Exception as e:
                    print(f"Error generating insight for column {col['name']}: {e}")
                    continue
        
        return insights
    
    def _generate_query_patterns(self, schema: Dict[str, Any]) -> List[str]:
        """Generate common query patterns for this table"""
        table_name = schema['table_name']
        columns = [col['name'] for col in schema['columns']]
        
        patterns = []
        
        # Basic patterns
        patterns.append(f"SELECT * FROM {table_name} LIMIT 10")
        patterns.append(f"SELECT COUNT(*) FROM {table_name}")
        
        # Column-specific patterns
        for col in schema['columns']:
            if col['unique_count'] < col['non_null_count'] * 0.5:  # Likely categorical
                patterns.append(f"SELECT {col['name']}, COUNT(*) FROM {table_name} GROUP BY {col['name']}")
            
            if col['type'].upper() in ['INTEGER', 'REAL', 'NUMERIC']:  # Numeric columns
                patterns.append(f"SELECT AVG({col['name']}), MIN({col['name']}), MAX({col['name']}) FROM {table_name}")
        
        return patterns[:5]  # Limit to 5 patterns
    
    def _generate_sql_examples(self, schema: Dict[str, Any]) -> List[str]:
        """Generate practical SQL examples"""
        table_name = schema['table_name']
        
        examples = [
            f"-- Get all records\nSELECT * FROM {table_name};",
            f"-- Count total records\nSELECT COUNT(*) as total_records FROM {table_name};"
        ]
        
        # Add column-specific examples
        for col in schema['columns'][:3]:  # First 3 columns
            if col['unique_count'] < 50:  # Categorical column
                examples.append(f"-- Group by {col['name']}\nSELECT {col['name']}, COUNT(*) as count FROM {table_name} GROUP BY {col['name']} ORDER BY count DESC;")
        
        return examples
    
    def _generate_database_context(self, tables: List[Dict], analyses: List[Dict]) -> Dict[str, Any]:
        """Generate overall database context"""
        
        # Create summary
        table_names = [t['table_name'] for t in tables]
        total_rows = sum(t['row_count'] for t in tables)
        
        summary = f"Database contains {len(tables)} tables with {total_rows} total records. Tables: {', '.join(table_names)}"
        
        # SQL context for LLM
        sql_context = "AVAILABLE TABLES AND COLUMNS:\n"
        for analysis in analyses:
            sql_context += f"\nTable: {analysis['table_name']}\n"
            sql_context += f"Description: {analysis['description']}\n"
            sql_context += "Columns:\n"
            for col in analysis['columns']:
                sql_context += f"  - {col['name']} ({col['type']})\n"
        
        # Query examples
        query_examples = []
        for analysis in analyses:
            query_examples.extend(analysis['sql_examples'][:2])  # 2 per table
        
        return {
            'summary': summary,
            'sql_context': sql_context,
            'query_examples': query_examples[:10],  # Limit total examples
            'relationships': self._detect_relationships(analyses)
        }
    
    def _detect_relationships(self, analyses: List[Dict]) -> List[str]:
        """Detect potential relationships between tables"""
        relationships = []
        
        # Simple relationship detection based on column names
        all_columns = {}
        for analysis in analyses:
            table_name = analysis['table_name']
            for col in analysis['columns']:
                col_name = col['name']
                if col_name not in all_columns:
                    all_columns[col_name] = []
                all_columns[col_name].append(table_name)
        
        # Find shared columns (potential relationships)
        for col_name, tables in all_columns.items():
            if len(tables) > 1:
                relationships.append(f"Column '{col_name}' appears in tables: {', '.join(tables)}")
        
        return relationships
    
    def get_table_context_for_prompt(self, user_prompt: str) -> str:
        """
        Get relevant table context for a specific user prompt
        
        Args:
            user_prompt: User's natural language query
            
        Returns:
            Formatted context string for prompt enhancement
        """
        schema_analysis = self.analyze_complete_schema()
        
        if not schema_analysis['tables']:
            return "No database tables available."
        
        # For prototype, return all context (in production, would filter relevant tables)
        context = f"""
DATABASE SCHEMA CONTEXT:
{schema_analysis['sql_context']}

EXAMPLE QUERIES:
{chr(10).join(schema_analysis['query_examples'][:5])}

RELATIONSHIPS:
{chr(10).join(schema_analysis['relationships']) if schema_analysis['relationships'] else 'No relationships detected'}
"""
        
        return context