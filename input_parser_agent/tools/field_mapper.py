import re
import time
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from difflib import SequenceMatcher

@dataclass
class FieldMapping:
    """Represents a mapping between user term and database field"""
    user_term: str
    table_name: str
    column_name: str
    confidence: float
    mapping_type: str  # 'exact', 'fuzzy', 'semantic', 'relationship'
    full_path: str  # e.g., 'customers.name'

@dataclass
class MappingResult:
    """Result of field mapping operation"""
    mappings: List[FieldMapping]
    confidence: float
    suggested_tables: List[str]
    unmapped_terms: List[str]

class FieldMapper:
    """
    Field mapper for natural language to database fields

    Features:
    - Exact word matching
    - Fuzzy string matching (typos, variations)
    - Semantic similarity (revenue/income/sales)
    - Relationship inference (customer sales → customers + sales tables)
    - Confidence scoring
    - Multiple mapping strategies
    """
    
    def __init__(self, schema_cache: Dict[str, Dict]):
        self.schema_cache = schema_cache
        self.business_vocabulary = self._build_business_vocabulary()
        self.common_synonyms = self._build_synonyms()
        
    def _build_business_vocabulary(self) -> Dict[str, Set[str]]:
        """Build business vocabulary from schema"""
        vocabulary = {}
        
        for table_name, table_info in self.schema_cache.items():
            # Table name variations
            table_terms = {table_name, table_name.rstrip('s'), table_name + 's'}
            vocabulary[table_name] = table_terms
            
            # Column name variations
            for column_name in table_info['columns'].keys():
                column_terms = {column_name, column_name.replace('_', ' '), column_name.replace('_', '')}
                full_path = f"{table_name}.{column_name}"
                vocabulary[full_path] = column_terms
        
        return vocabulary
    
    def _build_synonyms(self) -> Dict[str, List[str]]:
        """Common business term synonyms"""
        return {
            'revenue': ['sales', 'income', 'earnings', 'money', 'amount'],
            'customer': ['client', 'user', 'buyer', 'purchaser'],
            'product': ['item', 'goods', 'merchandise'],
            'date': ['time', 'when', 'period'],
            'quantity': ['amount', 'count', 'number', 'qty'],
            'price': ['cost', 'value', 'rate'],
            'country': ['region', 'location', 'area', 'territory'],
            'name': ['title', 'label', 'identifier'],
            'email': ['contact', 'address'],
            'category': ['type', 'kind', 'group', 'class']
        }
    
    def _calculate_similarity(self, term1: str, term2: str) -> float:
        """Calculate similarity between two terms"""
        # Exact match
        if term1.lower() == term2.lower():
            return 1.0
        
        # Fuzzy matching using SequenceMatcher
        similarity = SequenceMatcher(None, term1.lower(), term2.lower()).ratio()
        
        # Boost for partial matches
        if term1.lower() in term2.lower() or term2.lower() in term1.lower():
            similarity = max(similarity, 0.7)
        
        return similarity
    
    def _find_exact_matches(self, user_terms: List[str]) -> List[FieldMapping]:
        """Find exact matches between user terms and database fields"""
        mappings = []
        
        for term in user_terms:
            term_lower = term.lower()
            
            for table_name, table_info in self.schema_cache.items():
                # Check table name match
                if term_lower == table_name.lower() or term_lower == table_name.lower().rstrip('s'):
                    mappings.append(FieldMapping(
                        user_term=term,
                        table_name=table_name,
                        column_name='*',  # Whole table
                        confidence=1.0,
                        mapping_type='exact',
                        full_path=table_name
                    ))
                
                # Check column matches
                for column_name in table_info['columns'].keys():
                    if term_lower == column_name.lower() or term_lower == column_name.replace('_', ' ').lower():
                        mappings.append(FieldMapping(
                            user_term=term,
                            table_name=table_name,
                            column_name=column_name,
                            confidence=1.0,
                            mapping_type='exact',
                            full_path=f"{table_name}.{column_name}"
                        ))
        
        return mappings
    
    def _find_fuzzy_matches(self, user_terms: List[str], min_confidence: float = 0.6) -> List[FieldMapping]:
        """Find fuzzy matches for terms that didn't match exactly"""
        mappings = []
        
        for term in user_terms:
            best_matches = []
            
            for table_name, table_info in self.schema_cache.items():
                # Table name fuzzy match
                table_similarity = self._calculate_similarity(term, table_name)
                if table_similarity >= min_confidence:
                    best_matches.append(FieldMapping(
                        user_term=term,
                        table_name=table_name,
                        column_name='*',
                        confidence=table_similarity,
                        mapping_type='fuzzy',
                        full_path=table_name
                    ))
                
                # Column fuzzy matches
                for column_name in table_info['columns'].keys():
                    column_similarity = self._calculate_similarity(term, column_name)
                    if column_similarity >= min_confidence:
                        best_matches.append(FieldMapping(
                            user_term=term,
                            table_name=table_name,
                            column_name=column_name,
                            confidence=column_similarity,
                            mapping_type='fuzzy',
                            full_path=f"{table_name}.{column_name}"
                        ))
            
            # Keep best matches for this term
            if best_matches:
                best_matches.sort(key=lambda x: x.confidence, reverse=True)
                mappings.extend(best_matches[:3])  # Top 3 matches per term
        
        return mappings
    
    def _find_semantic_matches(self, user_terms: List[str]) -> List[FieldMapping]:
        """Find semantic matches using business vocabulary"""
        mappings = []
        
        for term in user_terms:
            term_lower = term.lower()
            
            # Check synonyms
            for canonical_term, synonyms in self.common_synonyms.items():
                if term_lower in synonyms or term_lower == canonical_term:
                    # Find database fields that match the canonical term
                    for table_name, table_info in self.schema_cache.items():
                        for column_name in table_info['columns'].keys():
                            if canonical_term in column_name.lower():
                                mappings.append(FieldMapping(
                                    user_term=term,
                                    table_name=table_name,
                                    column_name=column_name,
                                    confidence=0.8,  # High confidence for semantic matches
                                    mapping_type='semantic',
                                    full_path=f"{table_name}.{column_name}"
                                ))
        
        return mappings
    
    def _infer_relationships(self, mappings: List[FieldMapping]) -> List[str]:
        """Infer related tables based on current mappings"""
        suggested_tables = set()
        
        for mapping in mappings:
            # Add the mapped table
            suggested_tables.add(mapping.table_name)
            
            # Add related tables through foreign keys
            if mapping.table_name in self.schema_cache:
                table_info = self.schema_cache[mapping.table_name]
                for relationship in table_info['relationships'].values():
                    if '.' in relationship:
                        related_table = relationship.split('.')[0]
                        suggested_tables.add(related_table)
        
        return list(suggested_tables)
    
    def _extract_terms(self, user_input: str) -> List[str]:
        """Extract meaningful terms from user input"""
        # Remove common stop words
        stop_words = {'show', 'me', 'get', 'find', 'the', 'by', 'of', 'and', 'or', 'in', 'on', 'at', 'to', 'for'}
        
        # Split and clean terms
        terms = re.findall(r'\b\w+\b', user_input.lower())
        meaningful_terms = [term for term in terms if term not in stop_words and len(term) > 2]
        
        return meaningful_terms
    
    def map_fields(self, user_input: str) -> MappingResult:
        """
        Map user input to database fields
        
        Args:
            user_input: Natural language query like "show customer sales by region"
            
        Returns:
            MappingResult with field mappings and suggestions
        """
        # Map user input to database fields
        start_time = time.time()
        
        # Extract terms and map fields
        user_terms = self._extract_terms(user_input)
        
        all_mappings = []
        
        # Strategy 1: Exact matches (highest priority)
        exact_mappings = self._find_exact_matches(user_terms)
        all_mappings.extend(exact_mappings)
        
        # Strategy 2: Fuzzy matches for unmatched terms
        exact_terms = {m.user_term for m in exact_mappings}
        remaining_terms = [term for term in user_terms if term not in exact_terms]
        
        if remaining_terms:
            fuzzy_mappings = self._find_fuzzy_matches(remaining_terms)
            all_mappings.extend(fuzzy_mappings)
        
        # Strategy 3: Semantic matches
        semantic_mappings = self._find_semantic_matches(user_terms)
        all_mappings.extend(semantic_mappings)
        
        # Remove duplicates and sort by confidence
        unique_mappings = {}
        for mapping in all_mappings:
            key = f"{mapping.user_term}:{mapping.full_path}"
            if key not in unique_mappings or mapping.confidence > unique_mappings[key].confidence:
                unique_mappings[key] = mapping
        
        final_mappings = list(unique_mappings.values())
        final_mappings.sort(key=lambda x: x.confidence, reverse=True)
        
        # Calculate overall confidence
        if final_mappings:
            overall_confidence = sum(m.confidence for m in final_mappings) / len(final_mappings)
        else:
            overall_confidence = 0.0
        
        # Infer related tables
        suggested_tables = self._infer_relationships(final_mappings)
        
        # Find unmapped terms
        mapped_terms = {m.user_term for m in final_mappings}
        unmapped_terms = [term for term in user_terms if term not in mapped_terms]
        
        mapping_time = (time.time() - start_time) * 1000
        
        return MappingResult(
            mappings=final_mappings,
            confidence=overall_confidence,
            suggested_tables=suggested_tables,
            unmapped_terms=unmapped_terms
        )
    
    def get_mapping_summary(self, result: MappingResult) -> Dict[str, any]:
        """Get a summary of mapping results"""
        mappings_by_type = {}
        for mapping in result.mappings:
            if mapping.mapping_type not in mappings_by_type:
                mappings_by_type[mapping.mapping_type] = []
            mappings_by_type[mapping.mapping_type].append(mapping)
        
        return {
            'total_mappings': len(result.mappings),
            'confidence': result.confidence,
            'mappings_by_type': {k: len(v) for k, v in mappings_by_type.items()},
            'suggested_tables': result.suggested_tables,
            'unmapped_terms': result.unmapped_terms
        }
