import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def apply_date_filter(data, start_date=None, end_date=None, date_column='DATE'):
    """Apply date range filter to the data"""
    if date_column not in data.columns:
        return data
    
    filtered_data = data.copy()
    
    # Handle the case when the column is not a datetime
    if filtered_data[date_column].dtype != 'datetime64[ns]':
        try:
            filtered_data[date_column] = pd.to_datetime(filtered_data[date_column], errors='coerce')
        except:
            # If conversion fails, return original data
            return data
    
    # Apply start date filter
    if start_date is not None:
        try:
            if isinstance(start_date, str):
                start_date = pd.to_datetime(start_date)
            filtered_data = filtered_data[filtered_data[date_column] >= start_date]
        except:
            # If filter fails, skip this filter
            pass
    
    # Apply end date filter
    if end_date is not None:
        try:
            if isinstance(end_date, str):
                end_date = pd.to_datetime(end_date)
            filtered_data = filtered_data[filtered_data[date_column] <= end_date]
        except:
            # If filter fails, skip this filter
            pass
    
    return filtered_data

def apply_categorical_filter(data, column, values):
    """Apply categorical filter to the data"""
    if column not in data.columns:
        return data
    
    if not values:
        return data
    
    # Convert values to string for comparison if they're not already
    if data[column].dtype != 'object':
        filtered_data = data[data[column].astype(str).isin([str(v) for v in values])]
    else:
        filtered_data = data[data[column].isin(values)]
    
    return filtered_data

def apply_numerical_filter(data, column, min_val=None, max_val=None):
    """Apply numerical range filter to the data"""
    if column not in data.columns:
        return data
    
    filtered_data = data.copy()
    
    # Convert column to numeric if possible
    if filtered_data[column].dtype not in ['int64', 'float64']:
        try:
            filtered_data[column] = pd.to_numeric(filtered_data[column], errors='coerce')
        except:
            # If conversion fails, return original data
            return data
    
    # Apply min value filter
    if min_val is not None:
        try:
            filtered_data = filtered_data[filtered_data[column] >= min_val]
        except:
            # If filter fails, skip this filter
            pass
    
    # Apply max value filter
    if max_val is not None:
        try:
            filtered_data = filtered_data[filtered_data[column] <= max_val]
        except:
            # If filter fails, skip this filter
            pass
    
    return filtered_data

def apply_all_filters(data, filters):
    """Apply all filters to the data"""
    filtered_data = data.copy()
    
    # Apply date filters
    if 'date_filter' in filters and filters['date_filter']:
        date_filter = filters['date_filter']
        filtered_data = apply_date_filter(
            filtered_data, 
            date_filter.get('start_date'), 
            date_filter.get('end_date'),
            date_filter.get('column', 'DATE')
        )
    
    # Apply categorical filters
    if 'categorical_filters' in filters and filters['categorical_filters']:
        for cat_filter in filters['categorical_filters']:
            filtered_data = apply_categorical_filter(
                filtered_data,
                cat_filter['column'],
                cat_filter['values']
            )
    
    # Apply numerical filters
    if 'numerical_filters' in filters and filters['numerical_filters']:
        for num_filter in filters['numerical_filters']:
            filtered_data = apply_numerical_filter(
                filtered_data,
                num_filter['column'],
                num_filter.get('min_val'),
                num_filter.get('max_val')
            )
    
    return filtered_data

def calculate_aggregations(data, group_by=None, metrics=None):
    """Calculate aggregations based on group by columns and metrics"""
    if data.empty:
        return pd.DataFrame()
    
    if group_by is None or not group_by:
        return data
    
    # Basic validation
    for col in group_by:
        if col not in data.columns:
            return data
    
    # If no metrics specified, count rows per group
    if metrics is None or not metrics:
        return data.groupby(group_by).size().reset_index(name='count')
    
    # Prepare aggregation dictionary
    agg_dict = {}
    for metric in metrics:
        column = metric.get('column')
        agg = metric.get('agg', 'sum')
        
        if column in data.columns:
            agg_dict[column] = agg
    
    # If no valid metrics, count rows
    if not agg_dict:
        return data.groupby(group_by).size().reset_index(name='count')
    
    # Calculate aggregations
    result = data.groupby(group_by).agg(agg_dict).reset_index()
    
    return result

def create_graph(graph_type, x_data, y_data, color_data=None, title=None):
    """Create a plotly graph based on the specified type and data"""
    # Set default title
    title = title or f"{graph_type.capitalize()} Chart"
    
    if graph_type == "bar":
        fig = px.bar(x=x_data, y=y_data, color=color_data, title=title)
    elif graph_type == "line":
        fig = px.line(x=x_data, y=y_data, color=color_data, title=title)
    elif graph_type == "scatter":
        fig = px.scatter(x=x_data, y=y_data, color=color_data, title=title)
    elif graph_type == "pie":
        fig = px.pie(names=x_data, values=y_data, title=title)
    else:
        # Default to bar chart
        fig = px.bar(x=x_data, y=y_data, color=color_data, title=title)
    
    # Update layout
    fig.update_layout(
        xaxis_title=x_data.name if hasattr(x_data, 'name') else "X-Axis",
        yaxis_title=y_data.name if hasattr(y_data, 'name') else "Y-Axis",
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="white",
        height=400
    )
    
    # Add grid lines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    
    return fig

def create_gauge_chart(value, max_val, title="Gauge Chart"):
    """Create a gauge chart for KPI visualization"""
    # Ensure value is within range
    value = min(max(0, value), max_val)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 16, 'color': '#1e40af'}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "#1e40af"},
            'bar': {'color': "#3b82f6"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, max_val * 0.33], 'color': '#dbeafe'},
                {'range': [max_val * 0.33, max_val * 0.67], 'color': '#93c5fd'},
                {'range': [max_val * 0.67, max_val], 'color': '#60a5fa'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.8
            }
        }
    ))
    
    # Update layout
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        font=dict(family="Arial", size=12)
    )
    
    return fig