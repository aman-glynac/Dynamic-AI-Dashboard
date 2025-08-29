"""
idempotency.py - Idempotency checker for duplicate error detection
"""
import time
import logging
from typing import Dict, Optional, Tuple, Any
from ..config import IDEMPOTENCY_TTL

logger = logging.getLogger(__name__)


class IdempotencyChecker:
    """Ensures idempotent error handling"""
    
    def __init__(self, ttl: int = IDEMPOTENCY_TTL):
        self.seen_errors: Dict[Tuple[str, str], Tuple[Dict, float]] = {}
        self.ttl = ttl
    
    def check_duplicate(self, query_id: str, error_code: str) -> Optional[Dict]:
        """
        Check if this error was recently processed
        
        Args:
            query_id: Query identifier
            error_code: Error code
            
        Returns:
            Previous result if duplicate, None otherwise
        """
        key = (query_id, error_code)
        if key in self.seen_errors:
            result, timestamp = self.seen_errors[key]
            if time.time() - timestamp < self.ttl:
                logger.info(f"Duplicate error detected: {key}")
                return result
            else:
                del self.seen_errors[key]
        return None
    
    def store_result(self, query_id: str, error_code: str, result: Dict):
        """
        Store processed error result
        
        Args:
            query_id: Query identifier
            error_code: Error code
            result: Processing result to store
        """
        key = (query_id, error_code)
        self.seen_errors[key] = (result, time.time())
        logger.debug(f"Stored idempotency record for {key}")
    
    def clear_expired(self):
        """Remove expired idempotency records"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.seen_errors.items()
            if current_time - timestamp >= self.ttl
        ]
        for key in expired_keys:
            del self.seen_errors[key]
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired idempotency records")