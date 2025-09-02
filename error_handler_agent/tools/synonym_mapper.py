"""
synonym_mapper.py - Field synonym mapping service
"""
import logging
from typing import Dict, List, Optional
from ..config import FIELD_SYNONYMS

logger = logging.getLogger(__name__)


class SynonymMapper:
    """Maps field synonyms for schema errors"""
    
    def __init__(self, custom_synonyms: Dict[str, List[str]] = None):
        # Start with default synonyms
        self.synonyms = FIELD_SYNONYMS.copy()
        
        # Add custom synonyms if provided
        if custom_synonyms:
            self.synonyms.update(custom_synonyms)
        
        # Build reverse mapping
        self.reverse_map = self._build_reverse_map()
    
    def _build_reverse_map(self) -> Dict[str, str]:
        """Build reverse mapping from synonym to base term"""
        reverse_map = {}
        for base, syns in self.synonyms.items():
            for syn in syns:
                reverse_map[syn] = base
            reverse_map[base] = base
        return reverse_map
    
    def find_mapping(self, missing_field: str, available_fields: List[str]) -> Optional[Dict[str, str]]:
        """
        Find field mapping using synonyms
        
        Args:
            missing_field: Field that wasn't found
            available_fields: List of available fields in schema
            
        Returns:
            Mapping dictionary if found, None otherwise
        """
        missing_lower = missing_field.lower()
        available_lower = {f.lower(): f for f in available_fields}
        
        # Direct match (case-insensitive)
        if missing_lower in available_lower:
            return {missing_field: available_lower[missing_lower]}
        
        # Check if missing field is a known synonym
        if missing_lower in self.reverse_map:
            base_term = self.reverse_map[missing_lower]
            
            # Look for base term or its synonyms in available fields
            candidates = [base_term] + self.synonyms.get(base_term, [])
            for candidate in candidates:
                if candidate.lower() in available_lower:
                    mapping = {missing_field: available_lower[candidate.lower()]}
                    logger.info(f"Found synonym mapping: {missing_field} -> {mapping[missing_field]}")
                    return mapping
        
        # Fuzzy matching (contains)
        for available in available_fields:
            if missing_lower in available.lower() or available.lower() in missing_lower:
                return {missing_field: available}
        
        return None
    
    def add_synonym_group(self, base_term: str, synonyms: List[str]):
        """
        Add a new synonym group
        
        Args:
            base_term: The canonical term
            synonyms: List of synonyms for the base term
        """
        self.synonyms[base_term] = synonyms
        self.reverse_map = self._build_reverse_map()
        logger.info(f"Added synonym group for '{base_term}' with {len(synonyms)} synonyms")
    
    def get_all_synonyms(self, term: str) -> List[str]:
        """
        Get all synonyms for a term
        
        Args:
            term: Term to find synonyms for
            
        Returns:
            List of synonyms (including the base term)
        """
        term_lower = term.lower()
        
        # Find base term
        base_term = self.reverse_map.get(term_lower, term_lower)
        
        # Get all synonyms
        synonyms = [base_term] + self.synonyms.get(base_term, [])
        return synonyms