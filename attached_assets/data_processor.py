import pandas as pd
import numpy as np
import os
import io
import time
from datetime import datetime
import traceback
from typing import Dict, List, Union, Tuple, Any, Optional

class DataProcessor:
    """
    Utility class for efficient data processing and filtering operations.
    Handles large datasets with optimized filtering and provides progress tracking.
    """
    
    def __init__(self):
        self.data = None
        self.filtered_data = None
        self.column_types = {}
        self.categorical_columns = []
        self.numerical_columns = []
        self.date_columns = []
        self.progress = 0
        self.status = "Ready"
        self.metadata = {}
    
    def load_data(self, file_content: bytes, file_name: str) -> Tuple[bool, str]:
        """
        Load data from various file formats (CSV, Excel, etc.)
        
        Args:
            file_content: The binary content of the file
            file_name: Name of the file with extension
            
        Returns:
            Tuple of (success, message)
        """
        try:
            self.status = "Loading data..."
            self.progress = 10
            
            # Determine file type from extension
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Create file-like object from content
            content_io = io.BytesIO(file_content)
            
            # Load data based on file type
            if file_ext == '.csv':
                # Try different encodings and delimiters
                try:
                    self.data = pd.read_csv(content_io, encoding='utf-8')
                except:
                    content_io.seek(0)
                    self.data = pd.read_csv(content_io, encoding='latin1')
            elif file_ext in ['.xlsx', '.xls']:
                self.data = pd.read_excel(content_io)
            elif file_ext == '.json':
                self.data = pd.read_json(content_io)
            else:
                return False, f"Unsupported file format: {file_ext}"
            
            self.progress = 30
            
            # Initial data cleaning
            # Remove completely empty columns
            self.data = self.data.dropna(axis=1, how='all')
            
            # Remove duplicate rows
            self.data = self.data.drop_duplicates()
            
            self.progress = 50
            
            # Analyze column types
            self._analyze_columns()
            
            self.progress = 70
            
            # Create initial filtered data (all data)
            self.filtered_data = self.data.copy()
            
            # Generate metadata
            self._generate_metadata()
            
            self.progress = 100
            self.status = "Data loaded successfully"
            
            return True, f"Successfully loaded {len(self.data)} rows and {len(self.data.columns)} columns"
            
        except Exception as e:
            self.status = "Error loading data"
            error_msg = str(e)
            print(f"Error loading data: {error_msg}")
            print(traceback.format_exc())
            return False, f"Error loading data: {error_msg}"
    
    def _analyze_columns(self):
        """Analyze and categorize columns by data type"""
        self.column_types = {}
        self.categorical_columns = []
        self.numerical_columns = []
        self.date_columns = []
        
        for col in self.data.columns:
            # Skip columns with all NaN values
            if self.data[col].isna().all():
                continue
                
            # Check if column might be a date
            if self._is_date_column(col):
                self.date_columns.append(col)
                self.column_types[col] = 'date'
            # Check if column is numerical
            elif pd.api.types.is_numeric_dtype(self.data[col]):
                self.numerical_columns.append(col)
                self.column_types[col] = 'numerical'
            # Otherwise treat as categorical
            else:
                self.categorical_columns.append(col)
                self.column_types[col] = 'categorical'
    
    def _is_date_column(self, column: str) -> bool:
        """Check if a column contains date values"""
        # First check if it's already a datetime
        if pd.api.types.is_datetime64_any_dtype(self.data[column]):
            return True
            
        # If it's a string column, try to parse as date
        if pd.api.types.is_string_dtype(self.data[column]):
            # Get non-null values
            sample = self.data[column].dropna().head(100)
            if len(sample) == 0:
                return False
                
            # Try to convert to datetime
            try:
                pd.to_datetime(sample, errors='raise')
                # If successful, convert the whole column
                self.data[column] = pd.to_datetime(self.data[column], errors='coerce')
                return True
            except:
                return False
                
        return False
    
    def _generate_metadata(self):
        """Generate metadata about the dataset"""
        if self.data is None:
            return
            
        self.metadata = {
            'row_count': len(self.data),
            'column_count': len(self.data.columns),
            'memory_usage': self.data.memory_usage(deep=True).sum() / (1024 * 1024),  # MB
            'column_types': self.column_types,
            'categorical_stats': {},
            'numerical_stats': {},
            'date_stats': {}
        }
        
        # Generate stats for categorical columns
        for col in self.categorical_columns:
            value_counts = self.data[col].value_counts().head(20).to_dict()
            unique_count = self.data[col].nunique()
            self.metadata['categorical_stats'][col] = {
                'unique_values': unique_count,
                'top_values': value_counts,
                'missing_values': self.data[col].isna().sum()
            }
            
        # Generate stats for numerical columns
        for col in self.numerical_columns:
            self.metadata['numerical_stats'][col] = {
                'min': float(self.data[col].min()) if not pd.isna(self.data[col].min()) else None,
                'max': float(self.data[col].max()) if not pd.isna(self.data[col].max()) else None,
                'mean': float(self.data[col].mean()) if not pd.isna(self.data[col].mean()) else None,
                'median': float(self.data[col].median()) if not pd.isna(self.data[col].median()) else None,
                'missing_values': int(self.data[col].isna().sum())
            }
            
        # Generate stats for date columns
        for col in self.date_columns:
            if not self.data[col].empty and not self.data[col].isna().all():
                min_date = self.data[col].min()
                max_date = self.data[col].max()
                self.metadata['date_stats'][col] = {
                    'min_date': min_date.strftime('%Y-%m-%d') if not pd.isna(min_date) else None,
                    'max_date': max_date.strftime('%Y-%m-%d') if not pd.isna(max_date) else None,
                    'missing_values': int(self.data[col].isna().sum())
                }
    
    def apply_filters(self, filters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Apply multiple filters to the data
        
        Args:
            filters: Dictionary of filters to apply
                {
                    'date_filters': {'column': 'Date', 'start': '2023-01-01', 'end': '2023-12-31'},
                    'categorical_filters': {'column': 'Category', 'values': ['A', 'B']},
                    'numerical_filters': {'column': 'Value', 'min': 10, 'max': 100}
                }
                
        Returns:
            Tuple of (success, message)
        """
        if self.data is None:
            return False, "No data loaded"
            
        try:
            self.status = "Applying filters..."
            self.progress = 10
            
            # Start with all data
            self.filtered_data = self.data.copy()
            
            # Track how many rows were filtered out
            initial_count = len(self.filtered_data)
            
            # Apply date filters
            if 'date_filters' in filters and filters['date_filters']:
                for date_filter in filters['date_filters']:
                    column = date_filter.get('column')
                    start_date = date_filter.get('start')
                    end_date = date_filter.get('end')
                    
                    if column and column in self.date_columns:
                        if start_date:
                            start_date = pd.to_datetime(start_date)
                            self.filtered_data = self.filtered_data[self.filtered_data[column] >= start_date]
                        
                        if end_date:
                            end_date = pd.to_datetime(end_date)
                            self.filtered_data = self.filtered_data[self.filtered_data[column] <= end_date]
            
            self.progress = 40
            
            # Apply categorical filters
            if 'categorical_filters' in filters and filters['categorical_filters']:
                for cat_filter in filters['categorical_filters']:
                    column = cat_filter.get('column')
                    values = cat_filter.get('values')
                    
                    if column and values and column in self.categorical_columns:
                        self.filtered_data = self.filtered_data[self.filtered_data[column].isin(values)]
            
            self.progress = 70
            
            # Apply numerical filters
            if 'numerical_filters' in filters and filters['numerical_filters']:
                for num_filter in filters['numerical_filters']:
                    column = num_filter.get('column')
                    min_val = num_filter.get('min')
                    max_val = num_filter.get('max')
                    
                    if column and column in self.numerical_columns:
                        if min_val is not None:
                            self.filtered_data = self.filtered_data[self.filtered_data[column] >= min_val]
                        
                        if max_val is not None:
                            self.filtered_data = self.filtered_data[self.filtered_data[column] <= max_val]
            
            self.progress = 100
            
            # Calculate how many rows were filtered out
            filtered_count = len(self.filtered_data)
            filtered_out = initial_count - filtered_count
            
            self.status = "Filters applied successfully"
            
            return True, f"Applied filters: {filtered_count} rows remaining ({filtered_out} filtered out)"
            
        except Exception as e:
            self.status = "Error applying filters"
            error_msg = str(e)
            print(f"Error applying filters: {error_msg}")
            print(traceback.format_exc())
            return False, f"Error applying filters: {error_msg}"
    
    def get_filter_options(self) -> Dict[str, Any]:
        """
        Get available filter options based on the loaded data
        
        Returns:
            Dictionary of filter options for UI
        """
        if self.data is None:
            return {}
            
        options = {
            'date_columns': [],
            'categorical_columns': [],
            'numerical_columns': []
        }
        
        # Date column options
        for col in self.date_columns:
            if not self.data[col].isna().all():
                min_date = self.data[col].min()
                max_date = self.data[col].max()
                
                options['date_columns'].append({
                    'column': col,
                    'min_date': min_date.strftime('%Y-%m-%d') if not pd.isna(min_date) else None,
                    'max_date': max_date.strftime('%Y-%m-%d') if not pd.isna(max_date) else None
                })
        
        # Categorical column options
        for col in self.categorical_columns:
            # Get unique values (limit to top 100 for performance)
            unique_values = self.data[col].dropna().unique()
            if len(unique_values) <= 100:  # Only include if reasonable number of categories
                options['categorical_columns'].append({
                    'column': col,
                    'values': sorted([str(val) for val in unique_values])
                })
        
        # Numerical column options
        for col in self.numerical_columns:
            if not self.data[col].isna().all():
                min_val = self.data[col].min()
                max_val = self.data[col].max()
                
                options['numerical_columns'].append({
                    'column': col,
                    'min': float(min_val) if not pd.isna(min_val) else None,
                    'max': float(max_val) if not pd.isna(max_val) else None
                })
        
        return options
    
    def get_aggregated_data(self, 
                           group_by: List[str], 
                           metrics: List[Dict[str, str]],
                           sort_by: Optional[str] = None,
                           ascending: bool = True,
                           limit: int = 1000) -> pd.DataFrame:
        """
        Get aggregated data for visualization
        
        Args:
            group_by: List of columns to group by
            metrics: List of metrics to calculate
                [{'column': 'Sales', 'agg': 'sum'}, {'column': 'Profit', 'agg': 'mean'}]
            sort_by: Column to sort by
            ascending: Sort order
            limit: Maximum number of rows to return
            
        Returns:
            Aggregated DataFrame
        """
        if self.filtered_data is None or self.filtered_data.empty:
            return pd.DataFrame()
            
        # Validate group_by columns exist
        valid_group_by = [col for col in group_by if col in self.filtered_data.columns]
        if not valid_group_by:
            return pd.DataFrame()
            
        # Create aggregation dictionary
        agg_dict = {}
        for metric in metrics:
            column = metric.get('column')
            agg = metric.get('agg', 'sum')
            
            if column in self.filtered_data.columns:
                agg_dict[column] = agg
        
        if not agg_dict:
            return pd.DataFrame()
            
        # Perform aggregation
        result = self.filtered_data.groupby(valid_group_by).agg(agg_dict).reset_index()
        
        # Sort if specified
        if sort_by and sort_by in result.columns:
            result = result.sort_values(by=sort_by, ascending=ascending)
            
        # Apply limit
        if limit and limit > 0:
            result = result.head(limit)
            
        return result
    
    def get_time_series_data(self, 
                            date_column: str, 
                            value_column: str,
                            category_column: Optional[str] = None,
                            agg_function: str = 'sum',
                            freq: str = 'M') -> pd.DataFrame:
        """
        Get time series data for visualization
        
        Args:
            date_column: Date column to use for time series
            value_column: Value column to aggregate
            category_column: Optional column to split series by category
            agg_function: Aggregation function ('sum', 'mean', etc.)
            freq: Frequency for resampling ('D' for daily, 'W' for weekly, 'M' for monthly, etc.)
            
        Returns:
            Time series DataFrame
        """
        if self.filtered_data is None or self.filtered_data.empty:
            return pd.DataFrame()
            
        # Validate columns exist
        if date_column not in self.date_columns or value_column not in self.filtered_data.columns:
            return pd.DataFrame()
            
        # Create a copy to avoid modifying the original
        df = self.filtered_data.copy()
        
        # Ensure date column is datetime
        df[date_column] = pd.to_datetime(df[date_column])
        
        # If category column is specified, create time series for each category
        if category_column and category_column in df.columns:
            # Group by date and category
            result = df.groupby([pd.Grouper(key=date_column, freq=freq), category_column])[value_column].agg(agg_function).reset_index()
            # Pivot to get categories as columns
            result = result.pivot(index=date_column, columns=category_column, values=value_column).reset_index()
            # Fill NaN values with 0
            result = result.fillna(0)
        else:
            # Group by date only
            result = df.groupby(pd.Grouper(key=date_column, freq=freq))[value_column].agg(agg_function).reset_index()
            
        return result
    
    def get_correlation_matrix(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Calculate correlation matrix for numerical columns
        
        Args:
            columns: List of columns to include (must be numerical)
            
        Returns:
            Correlation matrix DataFrame
        """
        if self.filtered_data is None or self.filtered_data.empty:
            return pd.DataFrame()
            
        # If no columns specified, use all numerical columns
        if not columns:
            columns = self.numerical_columns
        else:
            # Filter to only include numerical columns
            columns = [col for col in columns if col in self.numerical_columns]
            
        if not columns:
            return pd.DataFrame()
            
        # Calculate correlation matrix
        corr_matrix = self.filtered_data[columns].corr()
        
        return corr_matrix
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for the filtered data
        
        Returns:
            Dictionary of summary statistics
        """
        if self.filtered_data is None or self.filtered_data.empty:
            return {}
            
        summary = {
            'row_count': len(self.filtered_data),
            'numerical_stats': {},
            'categorical_stats': {},
            'date_stats': {}
        }
        
        # Numerical statistics
        for col in self.numerical_columns:
            if col in self.filtered_data.columns:
                summary['numerical_stats'][col] = {
                    'min': float(self.filtered_data[col].min()) if not pd.isna(self.filtered_data[col].min()) else None,
                    'max': float(self.filtered_data[col].max()) if not pd.isna(self.filtered_data[col].max()) else None,
                    'mean': float(self.filtered_data[col].mean()) if not pd.isna(self.filtered_data[col].mean()) else None,
                    'median': float(self.filtered_data[col].median()) if not pd.isna(self.filtered_data[col].median()) else None,
                    'std': float(self.filtered_data[col].std()) if not pd.isna(self.filtered_data[col].std()) else None
                }
        
        # Categorical statistics (top 5 values)
        for col in self.categorical_columns:
            if col in self.filtered_data.columns:
                value_counts = self.filtered_data[col].value_counts().head(5).to_dict()
                summary['categorical_stats'][col] = {
                    'unique_count': self.filtered_data[col].nunique(),
                    'top_values': value_counts
                }
        
        # Date statistics
        for col in self.date_columns:
            if col in self.filtered_data.columns and not self.filtered_data[col].isna().all():
                min_date = self.filtered_data[col].min()
                max_date = self.filtered_data[col].max()
                summary['date_stats'][col] = {
                    'min_date': min_date.strftime('%Y-%m-%d') if not pd.isna(min_date) else None,
                    'max_date': max_date.strftime('%Y-%m-%d') if not pd.isna(max_date) else None,
                    'range_days': (max_date - min_date).days if not pd.isna(min_date) and not pd.isna(max_date) else None
                }
        
        return summary

