"""
config.py - Configuration and constants for Error Handler Agent
"""
import logging
from typing import List, Dict


# Logging configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Validation requirements
REQUIRED_FIELDS = ["agent_id", "timestamp", "status", "data"]
REQUIRED_DATA_FIELDS = ["error_type", "error_code", "message", "query_id"]

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAYS = [1, 3, 5]  # seconds

# Cache configuration
CACHE_TTL = 3600  # 1 hour
IDEMPOTENCY_TTL = 300  # 5 minutes

# Error patterns for classification
ERROR_PATTERNS: Dict[str, List[str]] = {
    "input_error": [
        "ambiguous", "unclear", "missing parameter", "invalid input", "unspecified"
    ],
    "schema_error": [
        "field not found", "column missing", "schema mismatch", "unknown field", "attribute error"
    ],
    "query_error": [
        "timeout", "query failed", "database error", "aggregation error", "execution failed"
    ],
    "chart_error": [
        "incompatible chart", "visualization error", "chart type mismatch", "rendering failed"
    ],
    "system_error": [
        "service unavailable", "connection failed", "system outage", "network error"
    ],
    "validation_error": [
        "validation failed", "constraint violation", "invalid format", "type mismatch"
    ]
}

# Field synonym mappings
FIELD_SYNONYMS = {
    "revenue": ["sales", "income", "earnings", "total_sales", "net_revenue"],
    "customer": ["client", "user", "account", "customer_id", "client_id"],
    "product": ["item", "sku", "merchandise", "product_id", "product_code"],
    "date": ["time", "timestamp", "period", "created_at", "order_date"],
    "region": ["area", "location", "zone", "territory", "geography"],
    "quantity": ["qty", "amount", "count", "units", "volume"],
    "price": ["cost", "amount", "value", "unit_price", "price_per_unit"]
}

# Chart compatibility matrix
CHART_COMPATIBILITY = {
    ("pie", "date"): ["line", "bar", "area"],
    ("pie", "time"): ["line", "bar", "area"],
    ("line", "category"): ["bar", "pie", "column"],
    ("scatter", "single"): ["bar", "line"],
}

# Message templates
MESSAGE_TEMPLATES = {
    "input_error": "I need more details. {root_cause}. {suggestion}",
    "schema_error": "Field not found. {root_cause}. {suggestion}",
    "query_error": "Query issue: {root_cause}. {suggestion}",
    "chart_error": "{root_cause}. {suggestion}",
    "system_error": "Technical issue: {root_cause}. {suggestion}",
    "validation_error": "Invalid data: {root_cause}. {suggestion}",
    "default": "Error: {root_cause}. {suggestion}"
}