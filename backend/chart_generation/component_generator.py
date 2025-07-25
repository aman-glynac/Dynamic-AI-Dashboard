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
{json.dumps(chart_data[:5], indent=2)}  
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

REQUIREMENTS:
1. Generate a COMPLETE React functional component (not a template)
2. Include ALL necessary imports from 'react' and 'recharts'
3. Embed the data directly in the component (no props needed)
4. Choose the BEST chart type for this data and user request
5. Use Tailwind CSS classes for styling
6. Include error handling and loading states
7. Make it responsive with proper sizing
8. Add meaningful tooltips, labels, and formatting
9. Generate an appropriate PascalCase component name
10. Include proper axis labels, legends, and titles
11. IMPORTANT: Use React.createElement() calls instead of JSX syntax
12. IMPORTANT: Do not use JSX tags like <div> or <BarChart>, use React.createElement instead

EXAMPLE FORMAT:
Instead of: <div className="container">Hello</div>
Use: React.createElement('div', {className: 'container'}, 'Hello')

Instead of: <BarChart data={data}><Bar dataKey="value" /></BarChart>
Use: React.createElement(BarChart, {data: data}, React.createElement(Bar, {dataKey: 'value'}))

GENERATE THE COMPLETE COMPONENT CODE - NO PLACEHOLDERS, NO TEMPLATES!

The component should be ready to render immediately when executed.

Return your response as a JSON object:
{{
  "component_code": "/* Complete React component code here */",
  "component_name": "ComponentName",
  "chart_type": "bar|line|pie|scatter|table|area|etc"
}}

IMPORTANT: The component_code should be the ENTIRE React component as a string, ready to execute.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": generation_prompt}],
                temperature=0.2,
                max_tokens=4000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            result = self._extract_json_from_response(response_text)
            
            if result and 'component_code' in result:
                # Validate the generated code
                if self._validate_component_code(result['component_code']):
                    return result
                else:
                    print("Generated component failed validation")
                    return None
            
            return None
            
        except Exception as e:
            print(f"Error in LLM component generation: {e}")
            return None
    
    def _validate_component_code(self, component_code: str) -> bool:
        """Basic validation of generated component code"""
        
        if not component_code or len(component_code) < 100:
            return False
            
        required_patterns = [
            r'import.*React.*from.*[\'"]react[\'"]',
            r'import.*from.*[\'"]recharts[\'"]',
            r'const\s+\w+\s*=\s*\(\s*\)\s*=>\s*{',
            r'export\s+default'
        ]
        
        for pattern in required_patterns:
            if not re.search(pattern, component_code):
                print(f"Missing required pattern: {pattern}")
                return False
        
        # Check for dangerous code
        dangerous_patterns = [
            r'eval\s*\(',
            r'Function\s*\(',
            r'document\.write',
            r'innerHTML\s*='
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, component_code, re.IGNORECASE):
                print(f"Dangerous pattern found: {pattern}")
                return False
        
        return True
    
    def _extract_json_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from LLM response"""
        try:
            # Remove code block formatting if present
            if response_text.startswith('```'):
                response_text = re.sub(r'```[\w]*\n?', '', response_text).strip()
                response_text = response_text.replace('```', '').strip()
            
            # Find JSON object boundaries
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            
            # Try parsing entire response
            return json.loads(response_text)
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text (first 500 chars): {response_text[:500]}")
            return None
    
    def generate_fallback_component(self, processed_data: ProcessedData, error_message: str) -> ComponentGenerationResult:
        """Generate a simple fallback component when main generation fails"""
        
        chart_data = processed_data.chart_data if processed_data.success else []
        
        fallback_code = f'''import React from 'react';

const ErrorChart = () => {{
  const data = {json.dumps(chart_data[:10], default=str)};
  
  return (
    <div className="w-full h-full flex items-center justify-center p-4">
      <div className="text-center">
        <div className="text-red-500 text-lg mb-2">⚠️ Chart Generation Error</div>
        <div className="text-gray-600 text-sm mb-4">{error_message}</div>
        {{data.length > 0 && (
          <div className="bg-gray-50 p-4 rounded-lg max-w-md">
            <h4 className="font-medium mb-2">Available Data:</h4>
            <pre className="text-xs text-left overflow-auto">
              {{JSON.stringify(data.slice(0, 3), null, 2)}}
            </pre>
            {{data.length > 3 && (
              <div className="text-xs text-gray-500 mt-2">
                ... and {{data.length - 3}} more rows
              </div>
            )}}
          </div>
        )}}
      </div>
    </div>
  );
}};

export default ErrorChart;'''
        
        return ComponentGenerationResult(
            component_code=fallback_code,
            component_name="ErrorChart",
            chart_type="error",
            success=True
        )