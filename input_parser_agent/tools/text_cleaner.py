import re
import time
from typing import Dict, List, Set, Tuple
from difflib import get_close_matches

class TextCleaner:
    """
    Text cleaner for the Input Parser Agent
    Based on experimental results and best practices
    """
    
    def __init__(self):
        # Intent keywords (keep these always)
        self.intent_keywords = {
            'show', 'display', 'chart', 'graph', 'plot', 'visualization', 'viz',
            'analyze', 'analysis', 'compare', 'comparison', 'trend', 'trends',
            'breakdown', 'break', 'view', 'see', 'present', 'examine'
        }
        
        # Business entity vocabulary
        self.business_vocabulary = {
            'sales', 'revenue', 'income', 'profit', 'margin', 'earnings',
            'customer', 'client', 'user', 'buyer', 'purchaser',
            'product', 'item', 'goods', 'merchandise',
            'order', 'purchase', 'transaction', 'buy',
            'performance', 'metrics', 'kpi', 'results', 'data'
        }
        
        # Time vocabulary
        self.time_vocabulary = {
            'year', 'yearly', 'annual', 'month', 'monthly', 'quarter', 'quarterly',
            'day', 'daily', 'week', 'weekly', 'time', 'period', 'date',
            'q1', 'q2', 'q3', 'q4', 'jan', 'feb', 'mar', 'apr', 'may', 'jun',
            'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
        }
        
        # Aggregate vocabulary
        self.aggregate_vocabulary = {
            'total', 'sum', 'count', 'average', 'avg', 'max', 'min', 'median',
            'top', 'bottom', 'best', 'worst', 'highest', 'lowest'
        }
        
        # Grouping prepositions
        self.grouping_words = {'by', 'per', 'over', 'during', 'from', 'to', 'vs', 'versus'}
        
        # Common typo corrections (expandable)
        self.typo_corrections = {
            'reveue': 'revenue', 'revenu': 'revenue', 'revinue': 'revenue',
            'salse': 'sales', 'sale': 'sales', 'seles': 'sales',
            'custmer': 'customer', 'costumer': 'customer', 'cutomer': 'customer',
            'mnoth': 'month', 'mont': 'month', 'monht': 'month',
            'quater': 'quarter', 'quartly': 'quarterly',
            'margens': 'margins', 'margns': 'margins',
            'custmers': 'customers', 'costumers': 'customers'
        }
        
        # Noise words to remove
        self.noise_words = {
            'can', 'you', 'please', 'maybe', 'could', 'would', 'should',
            'want', 'need', 'like', 'i', 'me', 'we', 'us', 'my', 'our',
            'give', 'get', 'find', 'help', 'make', 'create', 'generate',
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'for', 'of', 'with',
            'some', 'any', 'all', 'each', 'every', 'this', 'that', 'these', 'those'
        }

    def clean_text(self, raw_input: str) -> Dict:
        """
        Main text cleaning function
        Returns comprehensive cleaning results
        """
        start_time = time.time()
        
        # Step 1: Basic normalization
        normalized = self._normalize_text(raw_input)
        
        # Step 2: Fix typos
        typo_corrected = self._fix_typos(normalized)
        
        # Step 3: Extract and categorize words
        word_analysis = self._analyze_words(typo_corrected)
        
        # Step 4: Smart filtering
        cleaned = self._smart_filter(word_analysis)
        
        # Step 5: Calculate confidence metrics
        confidence_metrics = self._calculate_confidence(word_analysis, raw_input)
        
        # Step 6: Detect intent
        intent_analysis = self._detect_intent(word_analysis)
        
        processing_time = time.time() - start_time
        
        return {
            'original_input': raw_input,
            'cleaned_input': cleaned,
            'processing_time_ms': processing_time * 1000,
            'confidence_score': confidence_metrics['overall'],
            'is_actionable': confidence_metrics['overall'] > 0.3,
            'detected_intent': intent_analysis['primary_intent'],
            'intent_confidence': intent_analysis['confidence'],
            'extracted_entities': word_analysis['entities'],
            'extracted_time_refs': word_analysis['time_refs'],
            'typos_fixed': word_analysis['typos_fixed'],
            'words_removed': word_analysis['noise_removed'],
            'processing_metadata': {
                'has_intent_keywords': len(word_analysis['intent_words']) > 0,
                'has_business_entities': len(word_analysis['entities']) > 0,
                'has_time_references': len(word_analysis['time_refs']) > 0,
                'word_count_original': len(raw_input.split()),
                'word_count_cleaned': len(cleaned.split())
            }
        }

    def _normalize_text(self, text: str) -> str:
        """Basic text normalization"""
        # Convert to lowercase and strip
        text = text.lower().strip()
        
        # Remove extra punctuation but keep meaningful ones
        text = re.sub(r'[^\w\s\-/]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text

    def _fix_typos(self, text: str) -> str:
        """Fix common typos using predefined corrections"""
        words = text.split()
        corrected_words = []
        
        for word in words:
            if word in self.typo_corrections:
                corrected_words.append(self.typo_corrections[word])
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)

    def _analyze_words(self, text: str) -> Dict:
        """Analyze and categorize words while preserving order"""
        words = text.split()
        original_words = text.split()
        
        analysis = {
            'intent_words': [],
            'entities': [],
            'time_refs': [],
            'aggregates': [],
            'grouping_words': [],
            'noise_words': [],
            'other_words': [],
            'typos_fixed': [],
            'noise_removed': [],
            'all_words_with_categories': []
        }
        
        # Check for typo fixes
        for word in original_words:
            if word in self.typo_corrections:
                analysis['typos_fixed'].append((word, self.typo_corrections[word]))
        
        # Categorize words and preserve order
        for word in words:
            word_info = {'word': word, 'category': 'other'}
            
            if word in self.intent_keywords:
                analysis['intent_words'].append(word)
                word_info['category'] = 'intent'
            elif word in self.business_vocabulary:
                analysis['entities'].append(word)
                word_info['category'] = 'entity'
            elif word in self.time_vocabulary:
                analysis['time_refs'].append(word)
                word_info['category'] = 'time'
            elif word in self.aggregate_vocabulary:
                analysis['aggregates'].append(word)
                word_info['category'] = 'aggregate'
            elif word in self.grouping_words:
                analysis['grouping_words'].append(word)
                word_info['category'] = 'grouping'
            elif word in self.noise_words:
                analysis['noise_words'].append(word)
                analysis['noise_removed'].append(word)
                word_info['category'] = 'noise'
            else:
                analysis['other_words'].append(word)
                word_info['category'] = 'other'
            
            analysis['all_words_with_categories'].append(word_info)
        
        return analysis

    def _smart_filter(self, word_analysis: Dict) -> str:
        """Smart filtering to keep meaningful words while preserving order"""
        # Filter out only explicit noise words, keep everything else in original order
        filtered_words = []
        for word_info in word_analysis['all_words_with_categories']:
            # Keep everything except explicit noise words
            if word_info['category'] != 'noise':
                # Also filter out very short words that aren't important
                if len(word_info['word']) > 2 or word_info['category'] in ['intent', 'entity', 'time', 'aggregate', 'grouping']:
                    filtered_words.append(word_info['word'])
        
        return ' '.join(filtered_words)

    def _calculate_confidence(self, word_analysis: Dict, original_input: str) -> Dict:
        """Calculate confidence scores"""
        # Intent score (0.4 weight)
        intent_score = min(len(word_analysis['intent_words']) / 2, 1.0)
        
        # Entity score (0.4 weight)
        entity_score = min(len(word_analysis['entities']) / 2, 1.0)
        
        # Time reference score (0.2 weight)
        time_score = min(len(word_analysis['time_refs']) / 1, 1.0)
        
        # Overall confidence
        overall = (intent_score * 0.4 + entity_score * 0.4 + time_score * 0.2)
        
        return {
            'intent_score': intent_score,
            'entity_score': entity_score,
            'time_score': time_score,
            'overall': overall
        }

    def _detect_intent(self, word_analysis: Dict) -> Dict:
        """Detect primary visualization intent"""
        intent_priorities = {
            'chart': ['chart', 'graph', 'plot', 'visualization', 'viz'],
            'show': ['show', 'display', 'present', 'view'],
            'analyze': ['analyze', 'analysis', 'examine'],
            'compare': ['compare', 'comparison', 'vs', 'versus'],
            'trend': ['trend', 'trends'],
            'breakdown': ['breakdown', 'break']
        }
        
        detected_intents = {}
        for intent_type, keywords in intent_priorities.items():
            score = sum(1 for word in word_analysis['intent_words'] if word in keywords)
            if score > 0:
                detected_intents[intent_type] = score
        
        if detected_intents:
            primary_intent = max(detected_intents.items(), key=lambda x: x[1])
            return {
                'primary_intent': primary_intent[0],
                'confidence': primary_intent[1] / len(word_analysis['intent_words']) if word_analysis['intent_words'] else 0,
                'all_intents': detected_intents
            }
        else:
            return {
                'primary_intent': 'unknown',
                'confidence': 0.0,
                'all_intents': {}
            }
