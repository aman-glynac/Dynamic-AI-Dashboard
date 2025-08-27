import sqlite3
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Optional PostgreSQL support
try:
    import psycopg2
    HAS_POSTGRESQL = True
except ImportError:
    HAS_POSTGRESQL = False

@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    db_type: str  # 'sqlite' or 'postgresql'
    connection_params: Dict[str, Any]
    schema_name: Optional[str] = None

class SchemaRetriever:
    """
    Database schema retriever

    Features:
    - Fast database introspection
    - Schema caching with TTL
    - Foreign key relationship mapping
    - Multi-database support (SQLite, PostgreSQL)
    - Graceful error handling
    """
    
    def __init__(self, database_config: DatabaseConfig):
        self.config = database_config
        self.schema_cache = {}
        self.cache_timestamp = None
        self.cache_ttl = 3600  # 1 hour
        
        # Validate database type
        if self.config.db_type.lower() not in ['sqlite', 'postgresql']:
            raise ValueError(f"Unsupported database type: {self.config.db_type}")
        
        if self.config.db_type.lower() == 'postgresql' and not HAS_POSTGRESQL:
            raise ImportError("PostgreSQL support requires psycopg2: pip install psycopg2-binary")
    
    def _is_cache_valid(self) -> bool:
        """Check if schema cache is still valid"""
        if self.cache_timestamp is None:
            return False
        return (time.time() - self.cache_timestamp) < self.cache_ttl
    
    def _get_sqlite_tables(self) -> List[str]:
        """Get all table names from SQLite database"""
        db_path = self.config.connection_params['database']
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            return [row[0] for row in cursor.fetchall()]
    
    def _get_sqlite_columns(self, table_name: str) -> Dict[str, Dict]:
        """Get column information for SQLite table"""
        db_path = self.config.connection_params['database']
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            
            columns = {}
            for row in cursor.fetchall():
                cid, name, data_type, notnull, default_value, pk = row
                columns[name] = {
                    'data_type': data_type,
                    'is_nullable': not bool(notnull),
                    'is_primary_key': bool(pk),
                    'default_value': default_value
                }
            return columns
    
    def _get_sqlite_relationships(self, table_name: str) -> Dict[str, str]:
        """Get foreign key relationships for SQLite table"""
        db_path = self.config.connection_params['database']
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            
            relationships = {}
            for row in cursor.fetchall():
                id, seq, foreign_table, from_col, to_col, on_update, on_delete, match = row
                relationships[from_col] = f"{foreign_table}.{to_col}"
            return relationships
    
    def _get_postgresql_tables(self) -> List[str]:
        """Get all table names from PostgreSQL"""
        if not HAS_POSTGRESQL:
            return []
        
        import psycopg2
        schema_name = self.config.schema_name or 'public'
        with psycopg2.connect(**self.config.connection_params) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_type = 'BASE TABLE'
            """, (schema_name,))
            return [row[0] for row in cursor.fetchall()]
    
    def _get_postgresql_columns(self, table_name: str) -> Dict[str, Dict]:
        """Get column information for PostgreSQL table"""
        if not HAS_POSTGRESQL:
            return {}
        
        import psycopg2
        schema_name = self.config.schema_name or 'public'
        with psycopg2.connect(**self.config.connection_params) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
            """, (schema_name, table_name))
            
            columns = {}
            for row in cursor.fetchall():
                name, data_type, is_nullable, default_value = row
                columns[name] = {
                    'data_type': data_type,
                    'is_nullable': is_nullable == 'YES',
                    'is_primary_key': False,
                    'default_value': default_value
                }
            return columns
    
    def _get_postgresql_relationships(self, table_name: str) -> Dict[str, str]:
        """Get foreign key relationships for PostgreSQL table"""
        if not HAS_POSTGRESQL:
            return {}
        
        import psycopg2
        schema_name = self.config.schema_name or 'public'
        with psycopg2.connect(**self.config.connection_params) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = %s
                    AND tc.table_schema = %s
            """, (table_name, schema_name))
            
            relationships = {}
            for row in cursor.fetchall():
                column_name, foreign_table, foreign_column = row
                relationships[column_name] = f"{foreign_table}.{foreign_column}"
            return relationships
    
    def get_full_schema(self, force_refresh: bool = False) -> Dict[str, Dict]:
        """
        Get complete database schema with caching
        
        Returns:
            Dict with table names as keys and table info as values
            Table info includes: columns, relationships, column_count, etc.
        """
        if not force_refresh and self._is_cache_valid():
            return self.schema_cache
        
        print("🔍 Loading database schema...")
        start_time = time.time()
        
        schema = {}
        
        try:
            # Get tables based on database type
            if self.config.db_type.lower() == 'sqlite':
                tables = self._get_sqlite_tables()
            else:  # postgresql
                tables = self._get_postgresql_tables()
            
            # Load each table's schema
            for table_name in tables:
                try:
                    if self.config.db_type.lower() == 'sqlite':
                        columns = self._get_sqlite_columns(table_name)
                        relationships = self._get_sqlite_relationships(table_name)
                    else:  # postgresql
                        columns = self._get_postgresql_columns(table_name)
                        relationships = self._get_postgresql_relationships(table_name)
                    
                    schema[table_name] = {
                        'columns': columns,
                        'relationships': relationships,
                        'column_count': len(columns),
                        'has_relationships': len(relationships) > 0
                    }
                    
                except Exception as e:
                    print(f"   ⚠️  Warning: Could not load table {table_name}: {e}")
                    continue
            
            # Cache the results
            self.schema_cache = schema
            self.cache_timestamp = time.time()
            
            load_time = (time.time() - start_time) * 1000
            print(f"   ✅ Loaded {len(schema)} tables in {load_time:.1f}ms")
            
            return schema
            
        except Exception as e:
            print(f"   ❌ Error loading schema: {e}")
            return {}
    
    def get_table_schema(self, table_name: str) -> Optional[Dict]:
        """Get schema for a specific table"""
        # Check cache first
        if table_name in self.schema_cache and self._is_cache_valid():
            return self.schema_cache[table_name]
        
        try:
            if self.config.db_type.lower() == 'sqlite':
                columns = self._get_sqlite_columns(table_name)
                relationships = self._get_sqlite_relationships(table_name)
            else:  # postgresql
                columns = self._get_postgresql_columns(table_name)
                relationships = self._get_postgresql_relationships(table_name)
            
            table_schema = {
                'columns': columns,
                'relationships': relationships,
                'column_count': len(columns),
                'has_relationships': len(relationships) > 0
            }
            
            # Cache this table
            self.schema_cache[table_name] = table_schema
            return table_schema
            
        except Exception as e:
            print(f"❌ Error loading table {table_name}: {e}")
            return None
    
    def search_tables_by_column(self, column_pattern: str) -> Dict[str, Dict]:
        """Find tables that contain columns matching the pattern"""
        if not self._is_cache_valid():
            self.get_full_schema()
        
        matching_tables = {}
        pattern_lower = column_pattern.lower()
        
        for table_name, table_info in self.schema_cache.items():
            for column_name in table_info['columns'].keys():
                if pattern_lower in column_name.lower():
                    matching_tables[table_name] = table_info
                    break
        
        return matching_tables
    
    def get_related_tables(self, table_name: str) -> List[str]:
        """Get tables that are related to the given table through foreign keys"""
        if not self._is_cache_valid():
            self.get_full_schema()
        
        related_tables = set()
        
        # Check if table exists
        if table_name not in self.schema_cache:
            return []
        
        table_info = self.schema_cache[table_name]
        
        # Tables this table references (foreign keys pointing out)
        for relationship in table_info['relationships'].values():
            if '.' in relationship:
                foreign_table = relationship.split('.')[0]
                related_tables.add(foreign_table)
        
        # Tables that reference this table (foreign keys pointing in)
        for other_table, other_info in self.schema_cache.items():
            if other_table == table_name:
                continue
            
            for relationship in other_info['relationships'].values():
                if '.' in relationship and relationship.split('.')[0] == table_name:
                    related_tables.add(other_table)
        
        return list(related_tables)
    
    def get_table_summary(self) -> Dict[str, int]:
        """Get a quick summary of all tables and their column counts"""
        if not self._is_cache_valid():
            self.get_full_schema()
        
        return {
            table_name: table_info['column_count'] 
            for table_name, table_info in self.schema_cache.items()
        }
