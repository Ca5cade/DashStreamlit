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
    'heatmap': 'Heatmap',
    'treemap': 'Treemap',
    'sunburst': 'Sunburst',
    'funnel': 'Funnel Chart',
    'waterfall': 'Waterfall Chart'
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
            fig = px.bar(df, x='x', y='y', color='color', title=title,
                       color_discrete_sequence=px.colors.qualitative.Plotly)
        else:
            fig = px.bar(df, x='x', y='y', title=title, 
                       color_discrete_sequence=px.colors.qualitative.Plotly)
    
    elif graph_type == 'line':
        if color_data is not None:
            fig = px.line(df, x='x', y='y', color='color', title=title,
                        markers=True, line_shape='spline',
                        color_discrete_sequence=px.colors.qualitative.Plotly)
        else:
            fig = px.line(df, x='x', y='y', title=title, markers=True, line_shape='spline',
                        color_discrete_sequence=px.colors.qualitative.Plotly)
    
    elif graph_type == 'scatter':
        if color_data is not None:
            fig = px.scatter(df, x='x', y='y', color='color', title=title,
                           size_max=15, opacity=0.7,
                           color_discrete_sequence=px.colors.qualitative.Plotly)
        else:
            fig = px.scatter(df, x='x', y='y', title=title, size_max=15, opacity=0.7,
                           color_discrete_sequence=px.colors.qualitative.Plotly)
    
    elif graph_type == 'pie':
        fig = px.pie(df, values='y', names='x', title=title,
                    color_discrete_sequence=px.colors.qualitative.Plotly)
        fig.update_traces(textposition='inside', textinfo='percent+label')
    
    elif graph_type == 'histogram':
        if color_data is not None:
            fig = px.histogram(df, x='x', y='y', color='color', title=title,
                             nbins=20, opacity=0.7,
                             color_discrete_sequence=px.colors.qualitative.Plotly)
        else:
            fig = px.histogram(df, x='x', title=title, nbins=20, opacity=0.7,
                             color_discrete_sequence=px.colors.qualitative.Plotly)
    
    elif graph_type == 'box':
        if color_data is not None:
            fig = px.box(df, x='x', y='y', color='color', title=title,
                       notched=True, points='all',
                       color_discrete_sequence=px.colors.qualitative.Plotly)
        else:
            fig = px.box(df, x='x', y='y', title=title, notched=True, points='all',
                       color_discrete_sequence=px.colors.qualitative.Plotly)
    
    elif graph_type == 'heatmap':
        # For heatmap, we need to pivot the data
        try:
            pivot_df = df.pivot_table(index='y', columns='x', values='color' if color_data is not None else 'y', 
                                    aggfunc='count')
            fig = px.imshow(pivot_df, title=title, color_continuous_scale='Viridis')
        except Exception as e:
            # Fallback to basic heatmap if pivot fails
            print(f"Error creating heatmap: {str(e)}")
            x_range = range(len(df['x'].unique()))
            y_range = range(len(df['y'].unique()))
            dummy_data = np.random.randn(len(y_range), len(x_range))
            fig = px.imshow(dummy_data, title=title + " (Error: Could not pivot data properly)")
    
    elif graph_type == 'treemap':
        fig = px.treemap(df, path=['x'], values='y', title=title,
                        color_discrete_sequence=px.colors.qualitative.Plotly)
        
    elif graph_type == 'sunburst':
        # For sunburst, we need at least two levels of hierarchy
        if color_data is not None:
            # Use color column as second level
            fig = px.sunburst(df, path=['x', 'color'], values='y', title=title,
                             color_discrete_sequence=px.colors.qualitative.Plotly)
        else:
            # Use y as values and fake a second level for hierarchy
            df['level2'] = 'Value'
            fig = px.sunburst(df, path=['x', 'level2'], values='y', title=title,
                             color_discrete_sequence=px.colors.qualitative.Plotly)
            
    elif graph_type == 'funnel':
        # Sort data for funnel chart
        df_sorted = df.sort_values('y', ascending=False)
        fig = go.Figure(go.Funnel(
            x=df_sorted['y'],
            y=df_sorted['x'],
            textposition="inside",
            textinfo="value+percent initial",
            opacity=0.8,
            marker={"color": px.colors.qualitative.Plotly}
        ))
        fig.update_layout(title=title)
        
    elif graph_type == 'waterfall':
        # Create cumulative sums for waterfall
        df = df.sort_values('y', ascending=False).reset_index(drop=True)
        fig = go.Figure(go.Waterfall(
            name="Waterfall", 
            orientation="v",
            measure=["relative"] * len(df),
            x=df['x'],
            y=df['y'],
            textposition="outside",
            text=df['y'],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": px.colors.qualitative.Plotly[1]}},
            increasing={"marker": {"color": px.colors.qualitative.Plotly[0]}},
            totals={"marker": {"color": px.colors.qualitative.Plotly[2]}}
        ))
        fig.update_layout(title=title)
        
    else:
        # Default to bar chart if type not recognized
        fig = px.bar(df, x='x', y='y', title=title + " (Fallback: Type not supported)",
                   color_discrete_sequence=px.colors.qualitative.Plotly)
    
    # Improve layout
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Add grid lines
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(255,255,255,0.1)')
    
    return fig

def create_gauge_chart(value, max_val, title="Gauge Chart"):
    """Create a gauge chart for KPI visualization"""
    
    # Calculate percentage
    percentage = min(100, max(0, (value / max_val) * 100)) if max_val > 0 else 0
    
    # Define colors based on percentage
    if percentage < 25:
        color = "#2dcecc"  # Good - primary color
    elif percentage < 50:
        color = "#74c7b8"  # Average
    elif percentage < 75:
        color = "#f2c85b"  # Warning
    else:
        color = "#e97254"  # Critical
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        number = {"valueformat": ",.0f", "font": {"size": 24}},
        domain = {'x': [0, 1], 'y': [0, 1]},
        delta = {'reference': 0.8 * max_val, 'increasing': {'color': "#e97254"}, 'decreasing': {'color': "#2dcecc"}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "white",
            'steps': [
                {'range': [0, 0.25 * max_val], 'color': 'rgba(45, 206, 204, 0.3)'},
                {'range': [0.25 * max_val, 0.5 * max_val], 'color': 'rgba(116, 199, 184, 0.3)'},
                {'range': [0.5 * max_val, 0.75 * max_val], 'color': 'rgba(242, 200, 91, 0.3)'},
                {'range': [0.75 * max_val, max_val], 'color': 'rgba(233, 114, 84, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 0.8 * max_val
            }
        }
    ))
    
    fig.update_layout(
        title=title,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=14),
        margin=dict(l=20, r=20, t=60, b=20),
        height=350
    )
    
    return fig
