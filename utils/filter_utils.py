import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def apply_date_filter(data, start_date=None, end_date=None, date_column='DATE'):
    """
    Apply date range filter to the data
    
    Args:
        data: DataFrame to filter
        start_date: Start date for filter (inclusive)
        end_date: End date for filter (inclusive)
        date_column: Column name containing date values
        
    Returns:
        Filtered DataFrame
    """
    if date_column not in data.columns:
        return data
    
    filtered_data = data.copy()
    
    # Convert string dates to datetime if needed
    if start_date and not isinstance(start_date, datetime):
        try:
            start_date = pd.to_datetime(start_date)
        except:
            start_date = None
    
    if end_date and not isinstance(end_date, datetime):
        try:
            end_date = pd.to_datetime(end_date)
        except:
            end_date = None
    
    # Apply filters
    if start_date:
        filtered_data = filtered_data[filtered_data[date_column] >= start_date]
    
    if end_date:
        filtered_data = filtered_data[filtered_data[date_column] <= end_date]
    
    return filtered_data

def apply_categorical_filter(data, column, values):
    """
    Apply categorical filter to the data
    
    Args:
        data: DataFrame to filter
        column: Column name to filter on
        values: List of values to include
        
    Returns:
        Filtered DataFrame
    """
    if column not in data.columns or not values:
        return data
    
    # Convert values to list if not already
    if not isinstance(values, list):
        values = [values]
    
    # Ensure values are strings for comparison
    values = [str(val) for val in values]
    
    # Apply filter
    return data[data[column].astype(str).isin(values)]

def apply_numerical_filter(data, column, min_val=None, max_val=None):
    """
    Apply numerical range filter to the data
    
    Args:
        data: DataFrame to filter
        column: Column name to filter on
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)
        
    Returns:
        Filtered DataFrame
    """
    if column not in data.columns:
        return data
    
    filtered_data = data.copy()
    
    # Apply filters
    if min_val is not None:
        filtered_data = filtered_data[filtered_data[column] >= min_val]
    
    if max_val is not None:
        filtered_data = filtered_data[filtered_data[column] <= max_val]
    
    return filtered_data

def apply_all_filters(data, date_filter=None, categorical_filters=None, numerical_filters=None):
    """
    Apply all filters to the data
    
    Args:
        data: DataFrame to filter
        date_filter: Dictionary with date filter parameters
        categorical_filters: List of dictionaries with categorical filter parameters
        numerical_filters: List of dictionaries with numerical filter parameters
        
    Returns:
        Filtered DataFrame
    """
    filtered_data = data.copy()
    
    # Apply date filter
    if date_filter and 'column' in date_filter:
        filtered_data = apply_date_filter(
            filtered_data,
            start_date=date_filter.get('start'),
            end_date=date_filter.get('end'),
            date_column=date_filter['column']
        )
    
    # Apply categorical filters
    if categorical_filters:
        for cat_filter in categorical_filters:
            if 'column' in cat_filter and 'values' in cat_filter:
                filtered_data = apply_categorical_filter(
                    filtered_data,
                    column=cat_filter['column'],
                    values=cat_filter['values']
                )
    
    # Apply numerical filters
    if numerical_filters:
        for num_filter in numerical_filters:
            if 'column' in num_filter:
                filtered_data = apply_numerical_filter(
                    filtered_data,
                    column=num_filter['column'],
                    min_val=num_filter.get('min'),
                    max_val=num_filter.get('max')
                )
    
    return filtered_data

def calculate_aggregations(data, group_by=None, metrics=None):
    """
    Calculate aggregations based on group by columns and metrics
    
    Args:
        data: DataFrame to aggregate
        group_by: List of columns to group by
        metrics: List of metrics to calculate
        
    Returns:
        Aggregated DataFrame
    """
    if not group_by or not metrics or data.empty:
        return data
    
    # Ensure all group_by columns exist
    existing_group_by = [col for col in group_by if col in data.columns]
    if not existing_group_by:
        return data
    
    # Ensure all metrics exist
    existing_metrics = [col for col in metrics if col in data.columns]
    if not existing_metrics:
        return data
    
    # Create aggregation dictionary
    agg_dict = {}
    for metric in existing_metrics:
        # For simplicity, use sum for all numeric metrics
        # Could be extended to support different aggregation methods
        agg_dict[metric] = 'sum'
    
    # Group and aggregate
    grouped_data = data.groupby(existing_group_by).agg(agg_dict).reset_index()
    
    return grouped_data
