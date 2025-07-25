import groq
import json
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()

class ContextExtractor:
    """Use LLM to generate rich context and insights from parsed file data"""
    
    def __init__(self):
        self.client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    def generate_context(self, file_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive context using LLM analysis
        
        Args:
            file_metadata: Parsed file metadata from FileParser
            
        Returns:
            Dict containing LLM-generated context and insights
        """
        
        # Create context for different aspects
        table_description = self._generate_table_description(file_metadata)
        column_insights = self._generate_column_insights(file_metadata)
        business_context = self._generate_business_context(file_metadata)
        query_suggestions = self._generate_query_suggestions(file_metadata)
        
        return {
            'file_info': {
                'file_name': file_metadata['file_name'],
                'file_path': file_metadata['file_path'],
                'row_count': file_metadata['row_count'],
                'column_count': file_metadata['column_count']
            },
            'table_description': table_description,
            'column_insights': column_insights,
            'business_context': business_context,
            'query_suggestions': query_suggestions,
            'raw_metadata': file_metadata
        }
    
    def _generate_table_description(self, metadata: Dict[str, Any]) -> str:
        """Generate overall table description"""
        prompt = f"""
        Analyze this dataset and provide a comprehensive description:
        
        File: {metadata['file_name']}
        Rows: {metadata['row_count']}
        Columns: {metadata['column_count']}
        
        Column names: {[col['name'] for col in metadata['columns']]}
        Sample data: {json.dumps(metadata['sample_data'][:2], indent=2)}
        
        Provide a clear, concise description of:
        1. What this dataset appears to represent
        2. The main entities or subjects
        3. The time period or scope (if apparent)
        4. The likely source or domain
        
        Keep it under 200 words and focus on what would help someone understand the data's purpose.
        """
        
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_column_insights(self, metadata: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate insights for each column"""
        column_insights = []
        
        for col in metadata['columns']:
            prompt = f"""
            Analyze this column from a dataset:
            
            Column name: {col['name']}
            Data type: {col['dtype']}
            Sample values: {col['sample_values']}
            Unique count: {col['unique_count']}
            Non-null count: {col['non_null_count']}
            
            Provide:
            1. A clear description of what this column represents
            2. The business meaning or purpose
            3. Any data quality observations
            4. Potential relationships with other data
            
            Be concise but informative (under 100 words).
            """
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            column_insights.append({
                'column_name': col['name'],
                'insight': response.choices[0].message.content.strip(),
                'data_type': col['dtype'],
                'sample_values': col['sample_values']
            })
        
        return column_insights
    
    def _generate_business_context(self, metadata: Dict[str, Any]) -> str:
        """Generate business context and use cases"""
        prompt = f"""
        Based on this dataset analysis, provide business context:
        
        Dataset: {metadata['file_name']}
        Columns: {[col['name'] for col in metadata['columns']]}
        Sample data: {json.dumps(metadata['sample_data'][:2], indent=2)}
        Summary: {metadata['summary_stats']}
        
        Provide:
        1. Likely business domain or industry
        2. Common use cases or analysis scenarios
        3. Key metrics or KPIs that could be derived
        4. Typical stakeholders who would use this data
        
        Focus on practical business applications. Keep under 150 words.
        """
        
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_query_suggestions(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate common query patterns and analysis suggestions"""
        prompt = f"""
        Based on this dataset, suggest 5-7 common analysis queries or questions that users might ask:
        
        Dataset: {metadata['file_name']}
        Columns: {[col['name'] for col in metadata['columns']]}
        Sample data: {json.dumps(metadata['sample_data'][:2], indent=2)}
        
        Provide natural language questions that would be common for this type of data.
        Examples: "Show me sales by month", "What are the top performing products"
        
        Return as a simple list, one question per line.
        """
        
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        
        # Split response into list of questions
        questions = [q.strip('- ').strip() for q in response.choices[0].message.content.strip().split('\n') if q.strip()]
        return questions[:7]  # Limit to 7 suggestions