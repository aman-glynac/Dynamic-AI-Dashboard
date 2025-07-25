import groq
import json
import re
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
from dataclasses import dataclass

from query_generation import ProcessedData

load_dotenv()

@dataclass
class ComponentGenerationResult:
    """Structure for component generation results"""
    component_code: str
    component_name: str
    chart_type: str
    success: bool
    error_message: Optional[str] = None

class ComponentGenerator:
    """Generate complete React components from processed data using pure LLM generation"""
    
    def __init__(self):
        self.client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    def generate_component(self, processed_data: ProcessedData, user_prompt: str) -> ComponentGenerationResult:
        """
        Generate complete React component from processed data using LLM
        
        Args:
            processed_data: Processed data from pipeline
            user_prompt: Original user prompt for context
            
        Returns:
            ComponentGenerationResult with generated component code
        """
        
        if not processed_data.success:
            return ComponentGenerationResult(
                component_code="",
                component_name="",
                chart_type="",
                success=False,
                error_message="Cannot generate component from failed data processing"
            )
        
        try:
            # Generate complete component using LLM
            component_result = self._generate_complete_component(processed_data, user_prompt)
            
            if not component_result:
                return ComponentGenerationResult(
                    component_code="",
                    component_name="",
                    chart_type="",
                    success=False,
                    error_message="LLM failed to generate component code"
                )
            
            return ComponentGenerationResult(
                component_code=component_result['component_code'],
                component_name=component_result['component_name'],
                chart_type=component_result['chart_type'],
                success=True
            )
            
        except Exception as e:
            return ComponentGenerationResult(
                component_code="",
                component_name="",
                chart_type="",
                success=False,
                error_message=f"Component generation error: {str(e)}"
            )
    
    def _generate_complete_component(self, processed_data: ProcessedData, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Generate complete React component code using LLM"""
        
        chart_data = processed_data.chart_data
        chart_config = processed_data.chart_config
        data_summary = processed_data.data_summary
        
        generation_prompt = f"""
You are an expert React developer. Generate a complete, self-contained React component for data visualization.

USER REQUEST: "{user_prompt}"

DATA TO VISUALIZE:
{json.dumps(chart_data[:5], indent=2, default=str)}  
(Sample of {len(chart_data)} total rows)

CHART CONFIGURATION:
- Chart Type: {chart_config.get('chart_type', 'auto-detect from data')}
- X-Axis: {chart_config.get('x_axis', 'auto-detect')}
- Y-Axis: {chart_config.get('y_axis', 'auto-detect')}
- Title: {chart_config.get('title', 'Generate appropriate title')}

DATA SUMMARY:
- Columns: {data_summary.get('column_names', [])}
- Rows: {data_summary.get('total_rows', 0)}
- Numeric columns: {data_summary.get('numeric_columns', 0)}
- Categorical columns: {data_summary.get('categorical_columns', 0)}

STRICT REQUIREMENTS:
1. Generate a COMPLETE React functional component that works standalone
2. DO NOT include any import statements - they will be provided automatically
3. Use only React hooks (useState, useEffect, etc.) and Recharts components
4. Embed the complete data array directly in the component
5. Use Tailwind CSS classes for styling
6. Choose the BEST chart type for this data and user request
7. Include error handling and loading states
8. Make it responsive with proper sizing
9. Add meaningful tooltips, labels, and formatting
10. Generate an appropriate PascalCase component name
11. Include proper axis labels, legends, and titles
12. The component must be ready to render immediately when executed
13. Handle empty or invalid data gracefully
14. Use proper TypeScript syntax if needed

IMPORTANT FORMATTING:
- Start the component with: const ComponentName = () => {{
- End with: }}; (no export statement needed)
- Ensure all JSX is properly formatted
- Use double quotes for string literals
- Properly close all JSX tags
- Include proper spacing and indentation

EXAMPLE STRUCTURE:
```javascript
const SalesChart = () => {{
  const data = [...your data here...];
  
  return (
    <div className="w-full h-full p-4">
      <h2 className="text-xl font-bold mb-4">Your Chart Title</h2>
      <ResponsiveContainer width="100%" height="90%">
        <BarChart data={{data}}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="category" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="value" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}};
```

Return your response as a JSON object:
{{
  "component_code": "/* Complete React component code here - NO IMPORTS */",
  "component_name": "ComponentName",
  "chart_type": "bar|line|pie|scatter|table|area|etc"
}}

CRITICAL: The component_code should be the ENTIRE React component as a string, ready to execute, with NO import statements.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": generation_prompt}],
                temperature=0.1,  # Lower temperature for more consistent code generation
                max_tokens=4000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            result = self._extract_json_from_response(response_text)
            
            if result and 'component_code' in result:
                # Clean and validate the generated code
                cleaned_code = self._clean_component_code(result['component_code'])
                
                if self._validate_component_code(cleaned_code):
                    result['component_code'] = cleaned_code
                    return result
                else:
                    print("Generated component failed validation")
                    return None
            
            return None
            
        except Exception as e:
            print(f"Error in LLM component generation: {e}")
            return None
    
    def _clean_component_code(self, component_code: str) -> str:
        """Clean and normalize the generated component code"""
        
        # Remove any stray import statements that might have been included
        cleaned = re.sub(r'import\s+.*?from\s+[\'"][^\'"]+[\'"];?\s*', '', component_code)
        
        # Remove any export statements
        cleaned = re.sub(r'export\s+default\s+\w+;?\s*$', '', cleaned, flags=re.MULTILINE)
        
        # Ensure proper spacing around JSX elements
        cleaned = re.sub(r'>\s*<', '>\n<', cleaned)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        
        # Ensure the component ends properly
        if not cleaned.strip().endswith('};'):
            if cleaned.strip().endswith('}'):
                cleaned = cleaned.strip() + ';'
            else:
                cleaned = cleaned.strip() + '\n};'
        
        return cleaned.strip()
    
    def _validate_component_code(self, component_code: str) -> bool:
        """Enhanced validation of generated component code"""
        
        if not component_code or len(component_code.strip()) < 50:
            print("Component code too short")
            return False
        
        # Check for required patterns
        required_patterns = [
            r'const\s+\w+\s*=\s*\(\s*\)\s*=>\s*{',  # Function component pattern
            r'return\s*\(',                           # Return statement
            r'<\w+',                                  # JSX elements
            r'};?\s*$',                              # Proper ending
        ]
        
        for pattern in required_patterns:
            if not re.search(pattern, component_code, re.MULTILINE | re.DOTALL):
                print(f"Missing required pattern: {pattern}")
                return False
        
        # Check for dangerous code
        dangerous_patterns = [
            r'eval\s*\(',
            r'Function\s*\(',
            r'document\.write',
            r'innerHTML\s*=',
            r'dangerouslySetInnerHTML',
            r'__html',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, component_code, re.IGNORECASE):
                print(f"Dangerous pattern found: {pattern}")
                return False
        
        # Check for proper JSX closing tags
        open_tags = re.findall(r'<(\w+)(?:\s+[^>]*)?>(?!.*<\/\1>)', component_code)
        self_closing = re.findall(r'<(\w+)(?:\s+[^>]*)?\/>', component_code)
        
        # Make sure we don't have unclosed tags (basic check)
        for tag in open_tags:
            if tag not in self_closing and tag.lower() not in ['br', 'img', 'input', 'hr']:
                close_pattern = f'</{tag}>'
                if close_pattern not in component_code:
                    print(f"Unclosed tag found: {tag}")
                    # Don't fail validation for this, as it might be a nested component
        
        return True
    
    def _extract_json_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from LLM response with better error handling"""
        try:
            # Remove code block formatting if present
            cleaned_text = response_text
            
            # Handle various markdown code block formats
            if '```json' in cleaned_text:
                start_marker = '```json'
                end_marker = '```'
                start_idx = cleaned_text.find(start_marker)
                if start_idx != -1:
                    start_idx += len(start_marker)
                    end_idx = cleaned_text.find(end_marker, start_idx)
                    if end_idx != -1:
                        cleaned_text = cleaned_text[start_idx:end_idx].strip()
            
            elif cleaned_text.startswith('```'):
                cleaned_text = re.sub(r'```[\w]*\n?', '', cleaned_text).strip()
                cleaned_text = cleaned_text.replace('```', '').strip()
            
            # Find JSON object boundaries
            start_idx = cleaned_text.find('{')
            end_idx = cleaned_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = cleaned_text[start_idx:end_idx]
                
                # Clean up the JSON string
                json_str = self._clean_json_response(json_str)
                
                return json.loads(json_str)
            
            return None
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text (first 500 chars): {response_text[:500]}")
            return None
    
    def _clean_json_response(self, json_str: str) -> str:
        """Clean JSON response by handling special characters in component code"""
        
        # Handle escaped quotes in component code
        # This is tricky because we need to preserve the JSON structure while allowing quotes in the code
        
        try:
            # First, try to parse as-is
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            pass
        
        # If that fails, try to fix common issues
        
        # Fix unescaped quotes in component code (basic approach)
        # Look for component_code field and escape quotes within it
        
        def escape_quotes_in_code(match):
            field_name = match.group(1)
            code_content = match.group(2)
            
            # Escape quotes in the code content, but preserve JSON structure
            escaped_content = code_content.replace('\\', '\\\\').replace('"', '\\"')
            
            return f'"{field_name}": "{escaped_content}"'
        
        # Pattern to match component_code field with its content
        pattern = r'"(component_code)"\s*:\s*"((?:[^"\\]|\\.)*)(?<!\\)"'
        
        try:
            fixed_json = re.sub(pattern, escape_quotes_in_code, json_str, flags=re.DOTALL)
            json.loads(fixed_json)
            return fixed_json
        except (json.JSONDecodeError, re.error):
            pass
        
        # If all else fails, return original
        return json_str
    
    def generate_fallback_component(self, processed_data: ProcessedData, error_message: str) -> ComponentGenerationResult:
        """Generate a simple fallback component when main generation fails"""
        
        chart_data = processed_data.chart_data if processed_data.success else []
        
        # Create a much simpler fallback that's guaranteed to work
        fallback_code = f'''const ErrorChart = () => {{
  const data = {json.dumps(chart_data[:10], default=str)};
  
  return (
    <div className="w-full h-full flex items-center justify-center p-4">
      <div className="text-center max-w-2xl">
        <div className="text-red-500 text-2xl mb-4">⚠️</div>
        <div className="text-lg font-semibold text-red-700 mb-2">Chart Generation Error</div>
        <div className="text-sm text-gray-600 mb-4 bg-gray-100 p-3 rounded">{error_message}</div>
        {{data && data.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-800 mb-2">Available Data Preview:</h4>
            <div className="text-xs font-mono text-left bg-white p-2 rounded overflow-auto max-h-32">
              <pre>{{JSON.stringify(data.slice(0, 3), null, 2)}}</pre>
            </div>
            {{data.length > 3 && (
              <div className="text-xs text-blue-600 mt-2">
                ... and {{data.length - 3}} more rows
              </div>
            )}}
          </div>
        )}}
        <div className="mt-4 text-xs text-gray-500">
          Try rephrasing your prompt or check the data source
        </div>
      </div>
    </div>
  );
}};'''
        
        return ComponentGenerationResult(
            component_code=fallback_code,
            component_name="ErrorChart",
            chart_type="error",
            success=True
        )