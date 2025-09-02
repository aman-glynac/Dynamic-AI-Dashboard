import os
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Optional Groq integration
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

@dataclass
class SessionContext:
    """Session context information"""
    session_id: str
    last_query: Optional[str] = None
    last_tables: List[str] = None
    last_metrics: List[str] = None
    last_dimensions: List[str] = None
    user_preferences: Dict[str, Any] = None
    query_history: List[Dict] = None

@dataclass
class SchemaContext:
    """Schema context information"""
    available_tables: List[str]
    table_relationships: Dict[str, List[str]]
    suggested_tables: List[str]
    field_mappings: List[Dict]
    confidence_score: float

@dataclass
class AIIntent:
    """AI-detected intent information"""
    intent_type: str
    confidence: float
    suggested_chart: str
    reasoning: str
    metrics: List[str]
    dimensions: List[str]
    ai_enhanced: bool

@dataclass
class EnrichedInput:
    """Final enriched input with all context"""
    original_input: str
    cleaned_input: str
    validation_confidence: float
    schema_context: SchemaContext
    session_context: Optional[SessionContext]
    ai_intent: AIIntent
    metadata: Dict[str, Any]
    timestamp: datetime

class ContextInjector:
    """
    Context injector using Groq

    Features:
    - Groq AI for intelligent intent detection
    - Rule-based fallback system
    - Schema-aware AI prompting
    - Contextual understanding
    - Performance optimization
    """
    
    def __init__(self):
        self.session_store = {}
        self.groq_client = self._initialize_groq()
        self.rule_based_patterns = self._build_rule_patterns()
        
    def _initialize_groq(self) -> Optional[Any]:
        """Initialize Groq client if available"""
        if not HAS_GROQ:
            print("⚠️  Groq not available. Install with: pip install groq")
            return None
        
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key or api_key == 'your_groq_api_key_here':
            print("⚠️  GROQ_API_KEY not set. Using rule-based fallback.")
            return None
        
        try:
            return Groq(api_key=api_key)
        except Exception as e:
            print(f"⚠️  Failed to initialize Groq: {e}")
            return None
    
    def _build_rule_patterns(self) -> Dict[str, Dict]:
        """Rule-based patterns as fallback"""
        return {
            'show_data': {
                'keywords': ['show', 'display', 'get', 'find', 'view', 'list'],
                'chart': 'table',
                'confidence': 0.7
            },
            'compare_data': {
                'keywords': ['compare', 'vs', 'versus', 'difference', 'against'],
                'chart': 'bar',
                'confidence': 0.8
            },
            'trend_analysis': {
                'keywords': ['trend', 'over time', 'by date', 'monthly', 'yearly', 'timeline'],
                'chart': 'line',
                'confidence': 0.85
            },
            'distribution': {
                'keywords': ['distribution', 'breakdown', 'by category', 'by type', 'proportion'],
                'chart': 'pie',
                'confidence': 0.75
            },
            'correlation': {
                'keywords': ['relationship', 'correlation', 'scatter', 'association'],
                'chart': 'scatter',
                'confidence': 0.8
            }
        }
    
    def _build_ai_prompt(self, cleaned_input: str, schema_context: SchemaContext, session_context: Optional[SessionContext] = None) -> str:
        """Build AI prompt with schema and context information"""
        
        # Available tables and columns
        schema_info = "Available database schema:\n"
        for table in schema_context.suggested_tables:
            schema_info += f"- {table}\n"
        
        # Field mappings
        mapping_info = "Field mappings detected:\n"
        for mapping in schema_context.field_mappings[:5]:  # Top 5 mappings
            mapping_info += f"- '{mapping.get('user_term', '')}' → {mapping.get('full_path', '')} (confidence: {mapping.get('confidence', 0):.2f})\n"
        
        # Session context
        context_info = ""
        if session_context and session_context.query_history:
            context_info = f"\nPrevious queries in this session:\n"
            for query in session_context.query_history[-3:]:  # Last 3 queries
                context_info += f"- {query.get('query', '')}\n"
        
        prompt = f"""
You are an expert data visualization AI assistant. Analyze the user's request and provide intelligent recommendations.

User Query: "{cleaned_input}"

{schema_info}

{mapping_info}

{context_info}

Based on this information, analyze the user's intent and respond with ONLY a valid JSON object:

{{
  "intent_type": "show_data|compare_data|trend_analysis|distribution|correlation|custom",
  "confidence": 0.85,
  "suggested_chart": "table|bar|line|pie|scatter|heatmap|area",
  "reasoning": "Brief explanation of your recommendation",
  "metrics": ["sales.revenue", "sales.quantity"],
  "dimensions": ["customers.country", "sales.sale_date"]
}}

Requirements:
- intent_type: Choose the best category for this request
- confidence: Your confidence level (0.0-1.0)
- suggested_chart: Best visualization type for this data
- reasoning: One sentence explanation
- metrics: Numeric fields that should be measured/aggregated
- dimensions: Categorical/date fields for grouping/filtering

Respond with ONLY valid JSON, no additional text:
"""
        return prompt
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response with error handling"""
        try:
            
            # Try to extract JSON from response
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            
            # Try to find JSON in the response
            start_idx = response_clean.find('{')
            end_idx = response_clean.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_clean[start_idx:end_idx+1]
                return json.loads(json_str)
            else:
                raise json.JSONDecodeError("No JSON found", response_clean, 0)
                
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON Parse Error: {e}")
            # Fallback parsing
            return {
                'intent_type': 'custom',
                'confidence': 0.5,
                'suggested_chart': 'auto',
                'reasoning': f'Could not parse AI response: {str(e)[:100]}',
                'metrics': [],
                'dimensions': []
            }
    
    def _detect_intent_with_ai(self, cleaned_input: str, schema_context: SchemaContext, session_context: Optional[SessionContext] = None) -> AIIntent:
        """Use AI to detect user intent"""
        
        if not self.groq_client:
            return self._detect_intent_rule_based(cleaned_input)
        
        try:
            print("   🤖 Using Groq AI for intent detection...")
            
            # Build AI prompt
            prompt = self._build_ai_prompt(cleaned_input, schema_context, session_context)
            
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=os.getenv('GROQ_MODEL', 'llama3-8b-8192'),
                temperature=float(os.getenv('GROQ_TEMPERATURE', '0.3')),
                max_tokens=int(os.getenv('GROQ_MAX_TOKENS', '512'))
            )
            
            # Parse response
            ai_response = self._parse_ai_response(response.choices[0].message.content)
            
            return AIIntent(
                intent_type=ai_response.get('intent_type', 'custom'),
                confidence=ai_response.get('confidence', 0.5),
                suggested_chart=ai_response.get('suggested_chart', 'auto'),
                reasoning=ai_response.get('reasoning', 'AI analysis'),
                metrics=ai_response.get('metrics', []),
                dimensions=ai_response.get('dimensions', []),
                ai_enhanced=True
            )
            
        except Exception as e:
            print(f"   ⚠️  AI detection failed: {e}")
            return self._detect_intent_rule_based(cleaned_input)
    
    def _detect_intent_rule_based(self, cleaned_input: str) -> AIIntent:
        """Fallback rule-based intent detection"""
        print("   🔧 Using rule-based fallback for intent detection...")
        
        input_lower = cleaned_input.lower()
        best_match = None
        best_score = 0
        
        for pattern_name, pattern_info in self.rule_based_patterns.items():
            score = 0
            for keyword in pattern_info['keywords']:
                if keyword in input_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = pattern_name
        
        if best_match:
            pattern = self.rule_based_patterns[best_match]
            return AIIntent(
                intent_type=best_match,
                confidence=pattern['confidence'] * (best_score / len(pattern['keywords'])),
                suggested_chart=pattern['chart'],
                reasoning=f"Rule-based detection: {best_score} keyword matches",
                metrics=[],
                dimensions=[],
                ai_enhanced=False
            )
        
        return AIIntent(
            intent_type='custom',
            confidence=0.3,
            suggested_chart='auto',
            reasoning="No clear pattern detected",
            metrics=[],
            dimensions=[],
            ai_enhanced=False
        )
    
    def _build_table_relationships(self, schema_cache: Dict[str, Dict], suggested_tables: List[str]) -> Dict[str, List[str]]:
        """Build relationships between suggested tables"""
        relationships = {}
        
        for table in suggested_tables:
            related_tables = []
            
            if table in schema_cache:
                table_info = schema_cache[table]
                
                # Find tables this table references
                for relationship in table_info.get('relationships', {}).values():
                    if '.' in relationship:
                        foreign_table = relationship.split('.')[0]
                        if foreign_table in suggested_tables and foreign_table not in related_tables:
                            related_tables.append(foreign_table)
                
                # Find tables that reference this table
                for other_table, other_info in schema_cache.items():
                    if other_table != table and other_table in suggested_tables:
                        for relationship in other_info.get('relationships', {}).values():
                            if '.' in relationship and relationship.split('.')[0] == table:
                                if other_table not in related_tables:
                                    related_tables.append(other_table)
                
                relationships[table] = related_tables
        
        return relationships
    
    def _get_session_context(self, session_id: str) -> Optional[SessionContext]:
        """Get session context from storage"""
        return self.session_store.get(session_id)
    
    def _update_session_context(self, session_id: str, enriched_input: EnrichedInput):
        """Update session context with current query information"""
        context = self.session_store.get(session_id, SessionContext(session_id=session_id))
        
        # Update context
        context.last_query = enriched_input.cleaned_input
        context.last_tables = enriched_input.schema_context.suggested_tables
        context.last_metrics = enriched_input.ai_intent.metrics
        context.last_dimensions = enriched_input.ai_intent.dimensions
        
        # Update query history
        if context.query_history is None:
            context.query_history = []
        
        context.query_history.append({
            'timestamp': enriched_input.timestamp.isoformat(),
            'query': enriched_input.cleaned_input,
            'tables': context.last_tables,
            'confidence': enriched_input.validation_confidence,
            'intent': enriched_input.ai_intent.intent_type
        })
        
        # Keep only last 10 queries
        context.query_history = context.query_history[-10:]
        
        self.session_store[session_id] = context
    
    def inject_context(
        self,
        original_input: str,
        cleaned_input: str,
        validation_result: Dict,
        field_mapping_result: Dict,
        schema_cache: Dict[str, Dict],
        session_id: Optional[str] = None
    ) -> EnrichedInput:
        """
        Inject AI-enhanced context into processed input
        """
        print(f"🤖 AI-Enhanced context injection for: '{cleaned_input}'")
        start_time = time.time()
        
        # Build schema context
        available_tables = list(schema_cache.keys())
        suggested_tables = field_mapping_result.get('suggested_tables', [])
        field_mappings = field_mapping_result.get('mappings', [])
        
        # Convert field mappings to dicts if they're objects
        if field_mappings and hasattr(field_mappings[0], '__dict__'):
            field_mappings = [mapping.__dict__ for mapping in field_mappings]
        
        table_relationships = self._build_table_relationships(schema_cache, suggested_tables)
        
        schema_context = SchemaContext(
            available_tables=available_tables,
            table_relationships=table_relationships,
            suggested_tables=suggested_tables,
            field_mappings=field_mappings,
            confidence_score=field_mapping_result.get('confidence', 0.0)
        )
        
        # Get session context
        session_context = None
        if session_id:
            session_context = self._get_session_context(session_id)
        
        # AI-powered intent detection
        ai_intent = self._detect_intent_with_ai(cleaned_input, schema_context, session_context)
        
        # Build metadata
        metadata = {
            'processing_time_ms': (time.time() - start_time) * 1000,
            'components_used': ['text_cleaner', 'input_validator', 'schema_retriever', 'field_mapper', 'ai_context_injector'],
            'validation_details': validation_result,
            'mapping_details': field_mapping_result,
            'ai_enhanced': ai_intent.ai_enhanced,
            'groq_available': self.groq_client is not None
        }
        
        # Create enriched input
        enriched_input = EnrichedInput(
            original_input=original_input,
            cleaned_input=cleaned_input,
            validation_confidence=validation_result.get('confidence', 0.0),
            schema_context=schema_context,
            session_context=session_context,
            ai_intent=ai_intent,
            metadata=metadata,
            timestamp=datetime.now()
        )
        
        # Update session context
        if session_id:
            self._update_session_context(session_id, enriched_input)
        
        context_time = (time.time() - start_time) * 1000
        print(f"   ✅ AI context injected in {context_time:.1f}ms")
        
        return enriched_input
    
    def get_context_summary(self, enriched_input: EnrichedInput) -> Dict[str, Any]:
        """Get a summary of context information"""
        return {
            'schema_tables': len(enriched_input.schema_context.available_tables),
            'suggested_tables': len(enriched_input.schema_context.suggested_tables),
            'field_mappings': len(enriched_input.schema_context.field_mappings),
            'confidence': enriched_input.schema_context.confidence_score,
            'ai_intent': enriched_input.ai_intent.intent_type,
            'ai_confidence': enriched_input.ai_intent.confidence,
            'suggested_chart': enriched_input.ai_intent.suggested_chart,
            'ai_enhanced': enriched_input.ai_intent.ai_enhanced,
            'has_session_context': enriched_input.session_context is not None,
            'processing_time': enriched_input.metadata['processing_time_ms']
        }
