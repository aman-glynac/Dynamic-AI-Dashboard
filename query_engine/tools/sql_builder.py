"""
SQL Builder Tool
Constructs SQL queries from visualization intents with proper aggregation
"""

from typing import Dict, Optional

class SQLBuilder:
    """Tool for constructing SQL queries from visualization intents"""
    
    def __init__(self):
        # Fixed metric mappings with proper aggregation functions
        self.metric_mapping = {
            'revenue': 'SUM(total_amount)',
            'sales': 'SUM(total_amount)',
            'profit': 'SUM(total_amount - discount_amount)',
            'orders': 'COUNT(*)',
            'quantity': 'SUM(quantity)',
            'customers': 'COUNT(DISTINCT user_id)',
            'users': 'COUNT(DISTINCT user_id)',
            'products': 'COUNT(DISTINCT product_id)',
            'avg_order': 'AVG(total_amount)',
            'total': 'SUM(total_amount)'
        }
        
        self.dimension_mapping = {
            'month': 'strftime("%Y-%m", sale_date)',
            'year': 'strftime("%Y", sale_date)',
            'quarter': '''CASE 
                WHEN CAST(strftime("%m", sale_date) AS INTEGER) <= 3 THEN strftime("%Y", sale_date) || "-Q1"
                WHEN CAST(strftime("%m", sale_date) AS INTEGER) <= 6 THEN strftime("%Y", sale_date) || "-Q2"
                WHEN CAST(strftime("%m", sale_date) AS INTEGER) <= 9 THEN strftime("%Y", sale_date) || "-Q3"
                ELSE strftime("%Y", sale_date) || "-Q4" END''',
            'region': 'region',
            'product': 'product_id',
            'category': 'products.category',
            'channel': 'sales_channel',
            'brand': 'products.brand',
            'status': 'products.status'
        }
    
    def build_query(self, intent_type: str, metric: str, dimension: Optional[str] = None,
                   filters: Optional[Dict] = None, limit: int = 100) -> str:
        """
        Build SQL query based on intent parameters
        
        Args:
            intent_type: Type of analysis (summary, trend, comparison)
            metric: What to measure (revenue, sales, etc.)
            dimension: How to group data (month, region, etc.)
            filters: Optional filters to apply
            limit: Maximum number of records
            
        Returns:
            SQL query string with proper aggregation
        """
        
        metric_lower = metric.lower()
        dimension_lower = dimension.lower() if dimension else None
        
        # Get SQL expressions
        sql_metric = self.metric_mapping.get(metric_lower, f'SUM({metric_lower})')
        sql_dimension = self.dimension_mapping.get(dimension_lower, dimension_lower) if dimension_lower else None
        
        # Base tables with joins
        base_tables = "sales LEFT JOIN products ON sales.product_id = products.product_id"
        
        if intent_type == 'summary' and not dimension:
            # Single value summary
            query = f"SELECT {sql_metric} as value FROM {base_tables}"
            
        elif dimension and intent_type in ['trend', 'comparison']:
            # Grouped analysis with proper aggregation
            query = f"""
            SELECT 
                {sql_dimension} as {dimension_lower},
                {sql_metric} as {metric_lower}
            FROM {base_tables}
            GROUP BY {sql_dimension}
            """
            
            # Order by dimension for trends, by metric for comparisons
            if intent_type == 'trend':
                query += f" ORDER BY {sql_dimension}"
            else:
                query += f" ORDER BY {sql_metric} DESC"
                
        else:
            # Default grouped query
            if dimension:
                query = f"""
                SELECT 
                    {sql_dimension} as {dimension_lower},
                    {sql_metric} as {metric_lower}
                FROM {base_tables}
                GROUP BY {sql_dimension}
                ORDER BY {sql_metric} DESC
                """
            else:
                query = f"SELECT {sql_metric} as value FROM {base_tables}"
        
        # Add filters if provided
        if filters:
            where_conditions = []
            for key, value in filters.items():
                if isinstance(value, str):
                    where_conditions.append(f"{key} = '{value}'")
                else:
                    where_conditions.append(f"{key} = {value}")
            
            if where_conditions:
                query += f" WHERE {' AND '.join(where_conditions)}"
        
        # Add limit for grouped queries
        if dimension and limit:
            query += f" LIMIT {limit}"
            
        return query.strip()