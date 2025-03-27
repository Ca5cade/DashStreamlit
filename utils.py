# Filter functions
import pandas as pd
import numpy as np
from datetime import datetime

def apply_date_filter(data, start_date=None, end_date=None, date_column='DATE'):
    """Apply date range filter to the data"""
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
    """Apply categorical filter to the data"""
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
    """Apply numerical range filter to the data"""
    if column not in data.columns:
        return data
    
    filtered_data = data.copy()
    
    # Apply filters
    if min_val is not None:
        filtered_data = filtered_data[filtered_data[column] >= min_val]
    
    if max_val is not None:
        filtered_data = filtered_data[filtered_data[column] <= max_val]
    
    return filtered_data

def apply_all_filters(data, filters):
    """Apply all filters to the data"""
    filtered_data = data.copy()
    
    # Apply date filter
    filtered_data = apply_date_filter(
        filtered_data,
        start_date=filters.get("start_date"),
        end_date=filters.get("end_date")
    )
    
    # Apply categorical filters
    if filters.get("chains"):
        if 'idchainemontage' in filtered_data.columns:
            filtered_data = apply_categorical_filter(filtered_data, 'idchainemontage', filters.get("chains"))
        elif 'IDchainemontage' in filtered_data.columns:
            filtered_data = apply_categorical_filter(filtered_data, 'IDchainemontage', filters.get("chains"))
        elif 'Chaine' in filtered_data.columns:
            filtered_data = apply_categorical_filter(filtered_data, 'Chaine', filters.get("chains"))
    
    if filters.get("operations"):
        filtered_data = apply_categorical_filter(filtered_data, 'Operation', filters.get("operations"))
    
    if filters.get("controllers"):
        if 'IDcontroleur' in filtered_data.columns:
            filtered_data = apply_categorical_filter(filtered_data, 'IDcontroleur', filters.get("controllers"))
        elif 'IDControleur' in filtered_data.columns:
            filtered_data = apply_categorical_filter(filtered_data, 'IDControleur', filters.get("controllers"))
        elif 'Controleur' in filtered_data.columns:
            filtered_data = apply_categorical_filter(filtered_data, 'Controleur', filters.get("controllers"))
    
    # Apply numerical filters
    if filters.get("cnq_min") is not None or filters.get("cnq_max") is not None:
        filtered_data = apply_numerical_filter(
            filtered_data, 
            'CNQ', 
            min_val=filters.get("cnq_min"), 
            max_val=filters.get("cnq_max")
        )
    
    if filters.get("cnq_pct_min") is not None or filters.get("cnq_pct_max") is not None:
        filtered_data = apply_numerical_filter(
            filtered_data, 
            'CNQ_Percentage', 
            min_val=filters.get("cnq_pct_min"), 
            max_val=filters.get("cnq_pct_max")
        )
    
    return filtered_data

def calculate_aggregations(data, group_by=None, metrics=None):
    """Calculate aggregations based on group by columns and metrics"""
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

# Graph creation functions
def create_graph(graph_type, x_data, y_data, color_data=None, title=None):
    """Create a plotly graph based on the specified type and data"""
    import plotly.express as px
    
    if not title:
        title = "Data Visualization"
    
    if graph_type == 'bar':
        fig = px.bar(
            x=x_data, 
            y=y_data, 
            color=color_data,
            title=title,
            template="plotly_dark"
        )
    elif graph_type == 'line':
        fig = px.line(
            x=x_data, 
            y=y_data, 
            color=color_data,
            title=title,
            template="plotly_dark",
            markers=True
        )
    elif graph_type == 'scatter':
        fig = px.scatter(
            x=x_data, 
            y=y_data, 
            color=color_data,
            title=title,
            template="plotly_dark"
        )
    elif graph_type == 'pie':
        fig = px.pie(
            names=x_data, 
            values=y_data,
            title=title,
            template="plotly_dark"
        )
    elif graph_type == 'histogram':
        fig = px.histogram(
            x=x_data,
            title=title,
            template="plotly_dark"
        )
    elif graph_type == 'box':
        fig = px.box(
            x=color_data, 
            y=y_data,
            title=title,
            template="plotly_dark"
        )
    elif graph_type == 'heatmap':
        # Need to create a matrix for heatmap
        # This is a simplified version
        pivot_data = pd.DataFrame({'x': x_data, 'y': y_data, 'value': y_data})
        pivot_table = pivot_data.pivot_table(index='x', columns='y', values='value', aggfunc='mean')
        fig = px.imshow(
            pivot_table,
            title=title,
            template="plotly_dark"
        )
    elif graph_type == 'treemap':
        fig = px.treemap(
            names=x_data, 
            parents=[""]*len(x_data), 
            values=y_data,
            title=title,
            template="plotly_dark"
        )
    else:
        # Default to bar chart
        fig = px.bar(
            x=x_data, 
            y=y_data, 
            color=color_data,
            title=title,
            template="plotly_dark"
        )
    
    # Improve chart appearance
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=80, b=40)
    )
    
    return fig

def create_gauge_chart(value, max_val, title="Gauge Chart"):
    """Create a gauge chart for KPI visualization"""
    import plotly.graph_objects as go
    
    if not max_val or max_val == 0:
        max_val = max(100, value * 2)
    
    # Calculate percentage for gauge
    percentage = min(100, (value / max_val) * 100)
    
    # Define gauge colors
    if percentage < 33:
        color = "green"
    elif percentage < 66:
        color = "orange"
    else:
        color = "red"
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": title},
        delta={"reference": max_val * 0.8},  # 80% of max as reference
        gauge={
            "axis": {"range": [None, max_val], "tickwidth": 1, "tickcolor": "white"},
            "bar": {"color": color},
            "bgcolor": "white",
            "borderwidth": 2,
            "bordercolor": "gray",
            "steps": [
                {"range": [0, max_val/3], "color": "green"},
                {"range": [max_val/3, max_val*2/3], "color": "orange"},
                {"range": [max_val*2/3, max_val], "color": "red"}
            ]
        }
    ))
    
    # Improve chart appearance
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=80, b=40),
        height=300
    )
    
    return fig