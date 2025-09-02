import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

class FileParser:
    """Parse CSV and Excel files to extract structured data information"""
    
    def __init__(self):
        self.supported_extensions = {'.csv', '.xlsx', '.xls'}
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a file and extract comprehensive metadata
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Dict containing file metadata and data analysis
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        
        # Read the file
        df = self._read_file(file_path)
        
        # Extract metadata
        metadata = {
            'file_path': str(path.absolute()),
            'file_name': path.name,
            'file_size': path.stat().st_size,
            'extension': path.suffix.lower(),
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': self._analyze_columns(df),
            'sample_data': self._get_sample_data(df),
            'data_types': self._get_data_types(df),
            'missing_values': self._get_missing_values(df),
            'summary_stats': self._get_summary_stats(df)
        }
        
        return metadata
    
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
            raise ValueError("Could not read CSV file with any encoding/separator combination")
        
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        
        else:
            raise ValueError(f"Unsupported file extension: {path.suffix}")
    
    def _analyze_columns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze each column in detail"""
        columns_info = []
        
        for col in df.columns:
            col_info = {
                'name': col,
                'dtype': str(df[col].dtype),
                'non_null_count': df[col].count(),
                'null_count': df[col].isnull().sum(),
                'unique_count': df[col].nunique(),
                'sample_values': df[col].dropna().head(5).tolist(),
            }
            
            # Add type-specific analysis
            if df[col].dtype in ['int64', 'float64']:
                col_info.update({
                    'min_value': df[col].min(),
                    'max_value': df[col].max(),
                    'mean_value': df[col].mean(),
                    'std_value': df[col].std()
                })
            
            elif df[col].dtype == 'object':
                col_info.update({
                    'avg_length': df[col].astype(str).str.len().mean(),
                    'max_length': df[col].astype(str).str.len().max(),
                    'common_values': df[col].value_counts().head(3).to_dict()
                })
            
            columns_info.append(col_info)
        
        return columns_info
    
    def _get_sample_data(self, df: pd.DataFrame, n_samples: int = 3) -> List[Dict]:
        """Get sample rows from the dataframe"""
        return df.head(n_samples).to_dict('records')
    
    def _get_data_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """Get data types for all columns"""
        return df.dtypes.astype(str).to_dict()
    
    def _get_missing_values(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get missing value counts per column"""
        return df.isnull().sum().to_dict()
    
    def _get_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get overall summary statistics"""
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': len(numeric_cols),
            'categorical_columns': len(categorical_cols),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'completeness': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        }
        
        if len(numeric_cols) > 0:
            summary['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        return summary