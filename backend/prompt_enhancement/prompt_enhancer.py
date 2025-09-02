import groq
import json
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
from dataclasses import dataclass

from knowledge_base import ChromaManager
from database import SchemaAnalyzer
from .templates import CONTEXT_ENHANCED_TEMPLATE, GENERIC_ENHANCED_TEMPLATE, METADATA_EXTRACTION_TEMPLATE

load_dotenv()

@dataclass
class EnhancementResult:
    """Structure for prompt enhancement results"""
    enhanced_prompt: str
    metadata: Dict[str, Any]
    data_sources: List[str]
    has_context: bool
    sql_context: str

class PromptEnhancer:
    """Enhance user prompts with context and visualization guidance"""
    
    def __init__(self):
        self.client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.chroma_manager = ChromaManager()
        self.schema_analyzer = SchemaAnalyzer()
    
    def enhance_prompt(self, user_prompt: str) -> EnhancementResult:
        """
        Enhance user prompt with context and best practices
        
        Args:
            user_prompt: Raw user prompt
            
        Returns:
            EnhancementResult with enhanced prompt and metadata
        """
        
        # Query knowledge base for relevant context
        relevant_contexts = self.chroma_manager.query_relevant_context(
            user_prompt, 
            n_results=3
        )
        
        # Debug prints
        print(f"DEBUG: Found {len(relevant_contexts)} contexts")
        if relevant_contexts:
            print(f"DEBUG: Best distance: {relevant_contexts[0].get('distance', 1.0)}")
            for i, ctx in enumerate(relevant_contexts):
                print(f"DEBUG: Context {i+1}: {ctx['metadata'].get('file_name', 'Unknown')} - Distance: {ctx.get('distance', 1.0)}")
        
        # Get database schema context
        schema_context = self.schema_analyzer.get_table_context_for_prompt(user_prompt)
        
        # Determine if we have good context
        has_context = len(relevant_contexts) > 0 and relevant_contexts[0].get('distance', 1.0) < 0.7
        
        if has_context or schema_context.strip() != "No database tables available.":
            enhanced_prompt, data_sources = self._enhance_with_context(
                user_prompt, 
                relevant_contexts,
                schema_context
            )
            has_context = True  # Consider schema context as valid context
        else:
            enhanced_prompt, data_sources = self._enhance_generic(user_prompt)
        
        # Extract metadata
        metadata = self._extract_metadata(enhanced_prompt)
        
        return EnhancementResult(
            enhanced_prompt=enhanced_prompt,
            metadata=metadata,
            data_sources=data_sources,
            has_context=has_context,
            sql_context=schema_context
        )
    
    def _enhance_with_context(self, user_prompt: str, contexts: List[Dict[str, Any]], schema_context: str) -> tuple[str, List[str]]:
        """Enhance prompt using knowledge base context and database schema"""
        
        # Format context information
        data_context = self._format_contexts(contexts) if contexts else "No specific file context available."
        data_sources = list(set([ctx['metadata'].get('file_name', 'Unknown') for ctx in contexts])) if contexts else []
        
        # Add database tables as data sources
        if "No database tables available." not in schema_context:
            data_sources.append("Database Tables")
        
        # Apply context enhancement template
        formatted_prompt = CONTEXT_ENHANCED_TEMPLATE.format(
            user_prompt=user_prompt,
            data_context=data_context,
            schema_context=schema_context
        )
        
        # Get enhanced prompt from LLM
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        enhanced_prompt = response.choices[0].message.content.strip()
        
        return enhanced_prompt, data_sources
    
    def _enhance_generic(self, user_prompt: str) -> tuple[str, List[str]]:
        """Enhance prompt with generic best practices"""
        
        formatted_prompt = GENERIC_ENHANCED_TEMPLATE.format(
            user_prompt=user_prompt
        )
        
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        enhanced_prompt = response.choices[0].message.content.strip()
        
        return enhanced_prompt, ["Generic Enhancement"]
    
    def _extract_metadata(self, enhanced_prompt: str) -> Dict[str, Any]:
        """Extract structured metadata from enhanced prompt"""
        
        formatted_prompt = METADATA_EXTRACTION_TEMPLATE.format(
            enhanced_prompt=enhanced_prompt
        )
        
        try:
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": formatted_prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            metadata_text = response.choices[0].message.content.strip()
            
            # Clean up response to extract JSON
            if metadata_text.startswith('```json'):
                metadata_text = metadata_text.replace('```json', '').replace('```', '').strip()
            elif metadata_text.startswith('```'):
                metadata_text = metadata_text.replace('```', '').strip()
            
            # Find JSON object in response
            start_idx = metadata_text.find('{')
            end_idx = metadata_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = metadata_text[start_idx:end_idx]
                metadata = json.loads(json_str)
            else:
                raise ValueError("No JSON object found in response")
            
            # Validate required fields
            required_fields = ['confidence_score', 'suggested_chart_types', 'data_requirements', 'complexity_level']
            for field in required_fields:
                if field not in metadata:
                    metadata[field] = self._get_default_metadata_value(field)
            
            return metadata
            
        except (json.JSONDecodeError, ValueError, Exception) as e:
            print(f"Error extracting metadata: {e}")
            print(f"Raw response: {metadata_text if 'metadata_text' in locals() else 'No response'}")
            return self._get_default_metadata()
    
    def _format_contexts(self, contexts: List[Dict[str, Any]]) -> str:
        """Format context information for template"""
        
        formatted_contexts = []
        
        for ctx in contexts:
            metadata = ctx['metadata']
            document = ctx['document']
            
            context_info = f"""
FILE: {metadata.get('file_name', 'Unknown')}
TYPE: {metadata.get('type', 'Unknown')}
RELEVANCE: {1 - ctx.get('distance', 1.0):.2f}
CONTENT: {document}
---"""
            formatted_contexts.append(context_info)
        
        return "\n".join(formatted_contexts)
    
    def _get_default_metadata(self) -> Dict[str, Any]:
        """Return default metadata when extraction fails"""
        return {
            "confidence_score": 0.5,
            "suggested_chart_types": ["bar", "line"],
            "data_requirements": ["data columns", "numeric values"],
            "complexity_level": "moderate",
            "estimated_load_time": "moderate"
        }
    
    def _get_default_metadata_value(self, field: str) -> Any:
        """Get default value for specific metadata field"""
        defaults = {
            "confidence_score": 0.5,
            "suggested_chart_types": ["bar", "line"],
            "data_requirements": ["data columns"],
            "complexity_level": "moderate",
            "estimated_load_time": "moderate"
        }
        return defaults.get(field, "unknown")
    
    def get_enhancement_stats(self) -> Dict[str, Any]:
        """Get statistics about enhancement performance"""
        
        # Get all files in knowledge base
        files = self.chroma_manager.list_available_files()
        
        return {
            "total_data_sources": len(files),
            "available_files": [f['file_name'] for f in files],
            "knowledge_base_status": "active" if len(files) > 0 else "empty"
        }