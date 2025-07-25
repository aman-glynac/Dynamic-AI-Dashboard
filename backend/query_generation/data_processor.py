import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json

from .query_executor import QueryExecutionResult
from .sql_generator import SQLGenerationResult

@dataclass
class ProcessedData:
    """Structure for processed data ready for visualization"""
    chart_data: List[Dict[str, Any]]
    chart_config: Dict[str, Any]
    data_summary: Dict[str, Any]
    processing_log: List[str]
    success: bool
    error_message: Optional[str] = None

class DataProcessor:
    """Process query results into chart-ready data with transformations"""
    
    def __init__(self):
        self.processing_log = []
    
    def process_query_results(
        self, 
        sql_result: SQLGenerationResult, 
        execution_results: List[QueryExecutionResult]
    ) -> ProcessedData:
        """
        Process query execution results into chart-ready data
        
        Args:
            sql_result: SQL generation result with processing steps
            execution_results: List of query execution results
            
        Returns:
            ProcessedData ready for visualization
        """
        
        self.processing_log = []
        
        # Filter successful results
        successful_results = [result for result in execution_results if result.success]
        
        if not successful_results:
            return ProcessedData(
                chart_data=[],
                chart_config={},
                data_summary={},
                processing_log=self.processing_log,
                success=False,
                error_message="No successful query results to process"
            )
        
        # Use the first successful result as primary data
        primary_result = successful_results[0]
        
        try:
            # Convert to DataFrame for processing
            df = pd.DataFrame(primary_result.data)
            
            if df.empty:
                return ProcessedData(
                    chart_data=[],
                    chart_config=sql_result.chart_config,
                    data_summary={},
                    processing_log=self.processing_log,
                    success=False,
                    error_message="Query returned no data"
                )
            
            self.processing_log.append(f"Loaded {len(df)} rows with columns: {list(df.columns)}")
            
            # Apply processing steps from SQL generation
            processed_df = self._apply_processing_steps(df, sql_result.processing_steps)
            
            # Format data for charts
            chart_data = self._format_for_chart(processed_df, sql_result.chart_config)
            
            # Generate data summary
            data_summary = self._generate_data_summary(processed_df, primary_result)
            
            # Enhance chart config with processed data insights
            enhanced_chart_config = self._enhance_chart_config(
                sql_result.chart_config, 
                processed_df
            )
            
            return ProcessedData(
                chart_data=chart_data,
                chart_config=enhanced_chart_config,
                data_summary=data_summary,
                processing_log=self.processing_log,
                success=True
            )
            
        except Exception as e:
            return ProcessedData(
                chart_data=[],
                chart_config={},
                data_summary={},
                processing_log=self.processing_log,
                success=False,
                error_message=f"Data processing error: {str(e)}"
            )
    
    def _apply_processing_steps(self, df: pd.DataFrame, processing_steps: List[Dict[str, Any]]) -> pd.DataFrame:
        """Apply processing steps to the DataFrame"""
        
        processed_df = df.copy()
        
        for step in processing_steps:
            step_type = step.get('type', '').lower()
            description = step.get('description', '')
            
            self.processing_log.append(f"Applying step: {description}")
            
            try:
                if step_type == 'aggregation':
                    processed_df = self._apply_aggregation(processed_df, step)
                elif step_type == 'filtering':
                    processed_df = self._apply_filtering(processed_df, step)
                elif step_type == 'transformation':
                    processed_df = self._apply_transformation(processed_df, step)
                elif step_type == 'sorting':
                    processed_df = self._apply_sorting(processed_df, step)
                else:
                    self.processing_log.append(f"Unknown processing step type: {step_type}")
                    
            except Exception as e:
                self.processing_log.append(f"Error in processing step '{description}': {str(e)}")
                continue
        
        return processed_df
    
    def _apply_aggregation(self, df: pd.DataFrame, step: Dict[str, Any]) -> pd.DataFrame:
        """Apply aggregation transformations"""
        details = step.get('details', '')
        
        # Simple aggregation logic based on details
        if 'group by' in details.lower():
            # Try to identify grouping column from first non-numeric column
            group_cols = df.select_dtypes(include=['object']).columns
            if len(group_cols) > 0:
                group_col = group_cols[0]
                numeric_cols = df.select_dtypes(include=['number']).columns
                
                if len(numeric_cols) > 0:
                    agg_dict = {col: 'sum' for col in numeric_cols}
                    result = df.groupby(group_col).agg(agg_dict).reset_index()
                    self.processing_log.append(f"Grouped by {group_col}, aggregated {len(numeric_cols)} numeric columns")
                    return result
        
        return df
    
    def _apply_filtering(self, df: pd.DataFrame, step: Dict[str, Any]) -> pd.DataFrame:
        """Apply filtering transformations"""
        details = step.get('details', '')
        
        # Basic filtering - remove null values from key columns
        initial_rows = len(df)
        df_filtered = df.dropna()
        
        if len(df_filtered) < initial_rows:
            self.processing_log.append(f"Filtered out {initial_rows - len(df_filtered)} rows with null values")
        
        return df_filtered
    
    def _apply_transformation(self, df: pd.DataFrame, step: Dict[str, Any]) -> pd.DataFrame:
        """Apply data transformations"""
        details = step.get('details', '')
        
        # Basic transformations
        df_transformed = df.copy()
        
        # Convert string numbers to actual numbers
        for col in df_transformed.columns:
            if df_transformed[col].dtype == 'object':
                try:
                    numeric_series = pd.to_numeric(df_transformed[col], errors='coerce')
                    if not numeric_series.isna().all():
                        df_transformed[col] = numeric_series
                        self.processing_log.append(f"Converted {col} to numeric")
                except:
                    continue
        
        return df_transformed
    
    def _apply_sorting(self, df: pd.DataFrame, step: Dict[str, Any]) -> pd.DataFrame:
        """Apply sorting transformations"""
        details = step.get('details', '')
        
        # Sort by first numeric column descending, or first column ascending
        if len(df) > 1:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                sort_col = numeric_cols[0]
                df_sorted = df.sort_values(by=sort_col, ascending=False)
                self.processing_log.append(f"Sorted by {sort_col} (descending)")
            else:
                sort_col = df.columns[0]
                df_sorted = df.sort_values(by=sort_col, ascending=True)
                self.processing_log.append(f"Sorted by {sort_col} (ascending)")
            
            return df_sorted
        
        return df
    
    def _format_for_chart(self, df: pd.DataFrame, chart_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format DataFrame for chart consumption"""
        
        chart_type = chart_config.get('chart_type', 'table')
        
        if chart_type == 'table':
            # For tables, return all data as-is
            return df.to_dict('records')
        
        # For charts, ensure we have appropriate x and y columns
        x_axis = chart_config.get('x_axis')
        y_axis = chart_config.get('y_axis')
        
        if x_axis and y_axis and x_axis in df.columns and y_axis in df.columns:
            # Return data with explicit x/y naming for charts
            chart_data = []
            for _, row in df.iterrows():
                chart_data.append({
                    'x': row[x_axis],
                    'y': row[y_axis],
                    x_axis: row[x_axis],  # Keep original column names too
                    y_axis: row[y_axis],
                    **{col: row[col] for col in df.columns if col not in [x_axis, y_axis]}
                })
            
            self.processing_log.append(f"Formatted data for {chart_type} chart with x={x_axis}, y={y_axis}")
            return chart_data
        
        # Fallback to raw data
        return df.to_dict('records')
    
    def _generate_data_summary(self, df: pd.DataFrame, query_result: QueryExecutionResult) -> Dict[str, Any]:
        """Generate summary statistics about the processed data"""
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': len(numeric_cols),
            'categorical_columns': len(categorical_cols),
            'execution_time': query_result.execution_time,
            'memory_usage': df.memory_usage(deep=True).sum(),
            'column_names': list(df.columns)
        }
        
        # Add statistics for numeric columns
        if len(numeric_cols) > 0:
            summary['numeric_stats'] = {}
            for col in numeric_cols:
                summary['numeric_stats'][col] = {
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'null_count': int(df[col].isnull().sum())
                }
        
        # Add info about categorical columns
        if len(categorical_cols) > 0:
            summary['categorical_stats'] = {}
            for col in categorical_cols[:3]:  # Limit to first 3
                summary['categorical_stats'][col] = {
                    'unique_count': int(df[col].nunique()),
                    'top_values': df[col].value_counts().head(3).to_dict()
                }
        
        return summary
    
    def _enhance_chart_config(self, original_config: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """Enhance chart configuration based on processed data"""
        
        enhanced_config = original_config.copy()
        
        # Auto-detect better x/y columns if not specified or invalid
        if not enhanced_config.get('x_axis') or enhanced_config.get('x_axis') not in df.columns:
            # Use first categorical or first column as x-axis
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                enhanced_config['x_axis'] = categorical_cols[0]
            elif len(df.columns) > 0:
                enhanced_config['x_axis'] = df.columns[0]
        
        if not enhanced_config.get('y_axis') or enhanced_config.get('y_axis') not in df.columns:
            # Use first numeric column as y-axis
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                enhanced_config['y_axis'] = numeric_cols[0]
            elif len(df.columns) > 1:
                enhanced_config['y_axis'] = df.columns[1]
        
        # Suggest better chart type based on data
        if not enhanced_config.get('chart_type'):
            numeric_cols = df.select_dtypes(include=['number']).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
                enhanced_config['chart_type'] = 'bar'
            elif len(numeric_cols) >= 2:
                enhanced_config['chart_type'] = 'scatter'
            else:
                enhanced_config['chart_type'] = 'table'
        
        # Add data-driven suggestions
        enhanced_config['data_insights'] = {
            'recommended_limit': min(50, len(df)),  # Limit for performance
            'has_time_series': any('date' in col.lower() or 'time' in col.lower() for col in df.columns),
            'suggested_aggregation': len(df) > 100
        }
        
        return enhanced_config