import re
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class IntentType(Enum):
    VISUALIZATION = "visualization"
    COMPARISON = "comparison"
    TREND_ANALYSIS = "trend_analysis"
    FILTERING = "filtering"
    AGGREGATION = "aggregation"
    UNKNOWN = "unknown"


@dataclass
class ValidationResult:
    is_valid: bool
    confidence_score: float
    detected_intents: List[IntentType]
    primary_intent: IntentType
    data_elements: List[str]
    chart_type_hints: List[str]
    temporal_indicators: List[str]
    aggregation_hints: List[str]
    processing_time_ms: float
    validation_details: Dict


class InputValidator:
    """Advanced validation with weighted scoring and context awareness"""
    
    def __init__(self):
        self.intent_keywords = {
            'visualization': {
                'primary': ['show', 'display', 'chart', 'graph', 'plot', 'visualize'],
                'secondary': ['create', 'generate', 'make', 'build', 'draw', 'render', 'report'],
                'weight': 0.35
            },
            'data_references': {
                'metrics': ['sales', 'revenue', 'profit', 'income', 'count', 'total', 'average', 'performance', 'metrics'],
                'dimensions': ['customer', 'product', 'region', 'category', 'type'],
                'weight': 0.25
            },
            'temporal': {
                'periods': ['month', 'year', 'quarter', 'week', 'day'],
                'modifiers': ['monthly', 'yearly', 'quarterly', 'weekly', 'daily'],
                'indicators': ['over time', 'timeline', 'trend', 'history'],
                'weight': 0.20
            },
            'chart_types': {
                'explicit': ['bar chart', 'line chart', 'pie chart', 'scatter plot'],
                'implicit': ['breakdown', 'distribution', 'comparison', 'trend'],
                'weight': 0.10
            },
            'actions': {
                'analysis': ['compare', 'analyze', 'breakdown', 'summarize'],
                'filters': ['filter', 'where', 'only', 'exclude'],
                'weight': 0.10
            }
        }
        
        # Negative indicators that reduce confidence
        self.negative_patterns = [
            r'\b(hello|hi|help|how|what|why|when|where)\b',
            r'\b(can you|could you|please|thank you)\b',
            r'\b(random|test|example|sample)\b'
        ]

    def validate(self, cleaned_input: str) -> ValidationResult:
        start_time = time.time()
        input_lower = cleaned_input.lower()
        
        total_score = 0.0
        validation_details = {}
        detected_intents = []
        data_elements = []
        chart_hints = []
        temporal_indicators = []
        aggregation_hints = []
        
        # Score each category
        for category, config in self.intent_keywords.items():
            category_score = 0.0
            matches = []
            
            for subcategory, keywords in config.items():
                if subcategory == 'weight':
                    continue
                    
                for keyword in keywords:
                    if keyword in input_lower:
                        category_score += 1.0
                        matches.append(keyword)
                        
                        # Categorize matches
                        if category == 'data_references':
                            data_elements.append(keyword)
                        elif category == 'temporal':
                            temporal_indicators.append(keyword)
                        elif category == 'chart_types':
                            chart_hints.append(keyword)
                        elif category == 'actions' and subcategory == 'analysis':
                            aggregation_hints.append(keyword)
            
            # Normalize and weight the score
            if matches:
                normalized_score = min(category_score / len(matches), 1.0)
                weighted_score = normalized_score * config['weight']
                total_score += weighted_score
                validation_details[category] = {
                    'matches': matches,
                    'score': weighted_score
                }
        
        # Apply negative indicators penalty
        negative_score = 0.0
        for pattern in self.negative_patterns:
            if re.search(pattern, input_lower):
                negative_score += 0.05
        
        final_score = max(0.0, total_score - negative_score)
        
        # Determine intents based on matches
        if validation_details.get('visualization', {}).get('matches'):
            detected_intents.append(IntentType.VISUALIZATION)
        if validation_details.get('temporal', {}).get('matches'):
            detected_intents.append(IntentType.TREND_ANALYSIS)
        if 'compare' in input_lower or 'vs' in input_lower:
            detected_intents.append(IntentType.COMPARISON)
        if validation_details.get('actions', {}).get('matches'):
            detected_intents.append(IntentType.AGGREGATION)
        
        primary_intent = detected_intents[0] if detected_intents else IntentType.UNKNOWN
        
        processing_time = (time.time() - start_time) * 1000
        
        return ValidationResult(
            is_valid=final_score >= 0.3,
            confidence_score=final_score,
            detected_intents=detected_intents,
            primary_intent=primary_intent,
            data_elements=list(set(data_elements)),
            chart_type_hints=list(set(chart_hints)),
            temporal_indicators=list(set(temporal_indicators)),
            aggregation_hints=list(set(aggregation_hints)),
            processing_time_ms=processing_time,
            validation_details=validation_details
        )
