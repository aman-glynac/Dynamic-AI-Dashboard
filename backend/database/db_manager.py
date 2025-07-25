import sqlite3
import pandas as pd
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

class DatabaseManager:
    """Manage SQLite database operations for loading CSV/Excel data"""
    
    def __init__(self, db_path: str = "data/prototype.db"):
        self.db_path = db_path
        self.db_dir = os.path.dirname(db_path)
        
        # Create data directory if it doesn't exist
        os.makedirs(self.db_dir, exist_ok=True)
        
        # Initialize database
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with metadata table"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create metadata table to track loaded files
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT UNIQUE NOT NULL,
                    file_path TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    row_count INTEGER,
                    column_count INTEGER,
                    description TEXT
                )
            """)
            
            conn.commit()
    
    def load_file_to_database(self, file_path: str, table_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Load CSV/Excel file into SQLite database
        
        Args:
            file_path: Path to the file
            table_name: Custom table name (optional)
            
        Returns:
            Dict with loading results
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate table name if not provided
        if table_name is None:
            table_name = self._generate_table_name(path.stem)
        
        # Read file into DataFrame
        df = self._read_file(file_path)
        
        # Clean column names for SQL compatibility
        df.columns = [self._clean_column_name(col) for col in df.columns]
        
        # Load into SQLite
        with sqlite3.connect(self.db_path) as conn:
            # Drop table if exists (for reloading)
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            # Load data
            df.to_sql(table_name, conn, index=False, if_exists='replace')
            
            # Update metadata
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO file_metadata 
                (file_name, file_path, table_name, row_count, column_count, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                path.name,
                str(path.absolute()),
                table_name,
                len(df),
                len(df.columns),
                f"Data loaded from {path.name}"
            ))
            
            conn.commit()
        
        return {
            'table_name': table_name,
            'file_name': path.name,
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'sample_data': df.head(3).to_dict('records')
        }
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get detailed schema information for a table"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            
            if not columns_info:
                raise ValueError(f"Table {table_name} not found")
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            sample_rows = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Format column information
            columns = []
            for col_info in columns_info:
                col_name = col_info[1]
                col_type = col_info[2]
                
                # Get column statistics
                cursor.execute(f"SELECT COUNT(DISTINCT {col_name}) FROM {table_name}")
                unique_count = cursor.fetchone()[0]
                
                cursor.execute(f"SELECT COUNT({col_name}) FROM {table_name} WHERE {col_name} IS NOT NULL")
                non_null_count = cursor.fetchone()[0]
                
                columns.append({
                    'name': col_name,
                    'type': col_type,
                    'unique_count': unique_count,
                    'non_null_count': non_null_count,
                    'null_count': row_count - non_null_count
                })
            
            return {
                'table_name': table_name,
                'columns': columns,
                'row_count': row_count,
                'column_count': len(columns),
                'sample_data': sample_rows[:3]
            }
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            return [dict(row) for row in rows]
    
    def get_all_tables(self) -> List[Dict[str, Any]]:
        """Get information about all tables in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all user tables (exclude metadata)
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name != 'file_metadata'
                ORDER BY name
            """)
            
            table_names = [row[0] for row in cursor.fetchall()]
            
            tables_info = []
            for table_name in table_names:
                try:
                    schema = self.get_table_schema(table_name)
                    
                    # Get file metadata if available
                    cursor.execute("""
                        SELECT file_name, file_path, loaded_at, description
                        FROM file_metadata 
                        WHERE table_name = ?
                    """, (table_name,))
                    
                    file_info = cursor.fetchone()
                    
                    tables_info.append({
                        'table_name': table_name,
                        'file_name': file_info[0] if file_info else 'Unknown',
                        'file_path': file_info[1] if file_info else 'Unknown',
                        'loaded_at': file_info[2] if file_info else 'Unknown',
                        'description': file_info[3] if file_info else '',
                        'row_count': schema['row_count'],
                        'column_count': schema['column_count'],
                        'columns': [col['name'] for col in schema['columns']]
                    })
                    
                except Exception as e:
                    print(f"Error getting schema for {table_name}: {e}")
                    continue
            
            return tables_info
    
    def _read_file(self, file_path: str) -> pd.DataFrame:
        """Read file based on extension"""
        path = Path(file_path)
        
        if path.suffix.lower() == '.csv':
            # Try different encodings and separators
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                for sep in [',', ';', '\t']:
                    try:
                        return pd.read_csv(file_path, encoding=encoding, sep=sep)
                    except:
                        continue
            raise ValueError("Could not read CSV file")
        
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        
        else:
            raise ValueError(f"Unsupported file extension: {path.suffix}")
    
    def _generate_table_name(self, file_stem: str) -> str:
        """Generate valid SQL table name from file name"""
        # Remove special characters and spaces
        table_name = re.sub(r'[^a-zA-Z0-9_]', '_', file_stem)
        
        # Ensure it starts with letter or underscore
        if not table_name[0].isalpha() and table_name[0] != '_':
            table_name = 'table_' + table_name
        
        return table_name.lower()
    
    def _clean_column_name(self, col_name: str) -> str:
        """Clean column name for SQL compatibility"""
        # Replace spaces and special characters with underscores
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', str(col_name))
        
        # Remove consecutive underscores
        clean_name = re.sub(r'_+', '_', clean_name)
        
        # Remove leading/trailing underscores
        clean_name = clean_name.strip('_')
        
        # Ensure it starts with letter or underscore
        if clean_name and not clean_name[0].isalpha() and clean_name[0] != '_':
            clean_name = 'col_' + clean_name
        
        # Handle empty names
        if not clean_name:
            clean_name = 'unnamed_column'
        
        return clean_name.lower()
    
    def delete_table(self, table_name: str) -> bool:
        """Delete a table and its metadata"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Drop the table
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                
                # Remove from metadata
                cursor.execute("DELETE FROM file_metadata WHERE table_name = ?", (table_name,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error deleting table {table_name}: {e}")
            return False
        

if __name__ == "__main__":

    db_manager = DatabaseManager()  # This creates data/prototype.db automatically
    result = db_manager.load_file_to_database(r"D:\Glynac\dad-prototype\vgsales.csv")
    print(result)