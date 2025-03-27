# If this file doesn't exist, we'll create it
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Define graph types
GRAPH_TYPES = {
    'bar': 'Bar Chart',
    'line': 'Line Chart',
    'scatter': 'Scatter Plot',
    'pie': 'Pie Chart',
    'histogram': 'Histogram',
    'box': 'Box Plot',
    'heatmap': 'Heatmap'
}

def create_graph(graph_type, x_data, y_data, color_data=None, title=None):
    """
    Create a plotly graph based on the specified type and data
    
    Args:
        graph_type: Type of graph to create
        x_data: Data for x-axis
        y_data: Data for y-axis
        color_data: Data for color grouping (optional)
        title: Graph title (optional)
        
    Returns:
        Plotly figure
    """
    # Create a DataFrame from the data
    df = pd.DataFrame({
        'x': x_data,
        'y': y_data
    })
    
    if color_data is not None:
        df['color'] = color_data
    
    # Set default title if not provided
    if title is None:
        title = f"{graph_type.capitalize()} Chart"
    
    # Create the appropriate graph based on type
    if graph_type == 'bar':
        if color_data is not None:
            fig = px.bar(df, x='x', y='y', color='color', title=title)
        else:
            fig = px.bar(df, x='x', y='y', title=title)
    
    elif graph_type == 'line':
        if color_data is not None:
            fig = px.line(df, x='x', y='y', color='color', title=title)
        else:
            fig = px.line(df, x='x', y='y', title=title)
    
    elif graph_type == 'scatter':
        if color_data is not None:
            fig = px.scatter(df, x='x', y='y', color='color', title=title)
        else:
            fig = px.scatter(df, x='x', y='y', title=title)
    
    elif graph_type == 'pie':
        fig = px.pie(df, values='y', names='x', title=title)
    
    elif graph_type == 'histogram':
        if color_data is not None:
            fig = px.histogram(df, x='x', y='y', color='color', title=title)
        else:
            fig = px.histogram(df, x='x', title=title)
    
    elif graph_type == 'box':
        if color_data is not None:
            fig = px.box(df, x='x', y='y', color='color', title=title)
        else:
            fig = px.box(df, x='x', y='y', title=title)
    
    elif graph_type == 'heatmap':
        # For heatmap, we need to pivot the data
        pivot_df = df.pivot_table(index='y', columns='x', values='color' if color_data is not None else 'y', 
                                 aggfunc='count')
        fig = px.imshow(pivot_df, title=title)
    
    else:
        # Default to bar chart if type not recognized
        fig = px.bar(df, x='x', y='y', title=title)
    
    # Improve layout
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

