"""Prompt templates for enhancement engine"""

CONTEXT_ENHANCED_TEMPLATE = """
You are an expert data visualization and SQL assistant. Create comprehensive instructions for generating both SQL queries and interactive charts.

USER REQUEST: "{user_prompt}"

AVAILABLE DATA CONTEXT:
{data_context}

DATABASE SCHEMA:
{schema_context}

TASK: Generate detailed instructions that include:

1. SQL QUERY GENERATION:
   - Write a specific SQL query using the exact table and column names provided
   - Use proper syntax for the SQLite database
   - Include appropriate WHERE clauses, JOINs, GROUP BY, and ORDER BY as needed
   - Ensure the query answers the user's request with the available data

2. DATA TRANSFORMATION:
   - Specify how to format the SQL results for visualization
   - Include any necessary data aggregation or calculation steps
   - Handle null values and data cleaning requirements

3. VISUALIZATION SPECIFICATIONS:
   - Recommend the most appropriate chart type(s) based on the data
   - Specify React/Recharts component configuration
   - Include axis labels, colors, and styling details
   - Add interactive features and tooltips

4. TECHNICAL IMPLEMENTATION:
   - Provide complete React component structure
   - Include error handling for database queries
   - Add responsive design considerations
   - Specify data loading and caching strategies

Generate a comprehensive response that enables creation of both the SQL query and the interactive visualization.
"""

GENERIC_ENHANCED_TEMPLATE = """
You are an expert data visualization assistant. Enhance this user request with comprehensive technical guidance.

USER REQUEST: "{user_prompt}"

Since no specific data context is available, provide general but detailed instructions that include:

1. COMMON DATA PATTERNS:
   - Suggest typical data structures that would support this request
   - Recommend standard column names and data types
   - Include common aggregation and filtering approaches

2. VISUALIZATION BEST PRACTICES:
   - Recommend appropriate chart types for this type of analysis
   - Specify optimal axis configurations and styling
   - Include interactive features that enhance user experience
   - Consider responsive design principles

3. TECHNICAL IMPLEMENTATION:
   - Provide React/Recharts component structure
   - Include data transformation and formatting guidelines
   - Specify error handling and loading states
   - Add accessibility considerations

4. SQL QUERY GUIDANCE:
   - Suggest general query patterns for this type of request
   - Include common JOINs, aggregations, and filters
   - Recommend performance optimization techniques
   - Consider data validation and edge cases

5. ADVANCED FEATURES:
   - Suggest drill-down capabilities if applicable
   - Include export and sharing functionality
   - Add real-time data update considerations
   - Recommend caching strategies

Generate comprehensive instructions that enable creation of both robust SQL queries and engaging interactive visualizations, even without specific schema knowledge.
"""

METADATA_EXTRACTION_TEMPLATE = """
Analyze this enhanced prompt and extract key metadata:

ENHANCED PROMPT: "{enhanced_prompt}"

Extract and return ONLY a JSON object with:
{{
  "confidence_score": <float between 0-1 indicating how well the request can be fulfilled>,
  "suggested_chart_types": [<list of recommended chart types>],
  "data_requirements": [<list of key data elements needed>],
  "complexity_level": "<simple|moderate|complex>",
  "estimated_load_time": "<fast|moderate|slow>"
}}

Return only valid JSON, no additional text.
"""