from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import numpy as np
import dash
from dash import html
import traceback

def register_callbacks(app, data):
    """Register callbacks for the main dashboard"""
    
    # Callback to update all visualizations based on filters
    @app.callback(
        [Output('cnq-value', 'children'),
         Output('cnq-percentage-value', 'children'),
         Output('gauge-chart', 'figure'),
         Output('pie-chart', 'figure'),
         Output('line-chart', 'figure')],
        [Input('filter-kwm', 'value'),
         Input('filter-period', 'start_date'),
         Input('filter-period', 'end_date'),
         Input('filter-order', 'value'),
         Input('filter-provider', 'value'),
         Input('filter-source', 'value')]
    )
    def update_dashboard(kwm_values, start_date, end_date, order_values, provider_values, source_values):
        try:
            print("Updating dashboard with filters:", {
                'kwm': kwm_values,
                'start_date': start_date,
                'end_date': end_date,
                'order': order_values,
                'provider': provider_values
            })
            
            # Start with all data
            filtered_data = data.copy()
            print("Initial data shape:", filtered_data.shape)
            
            # Apply filters
            if kwm_values:
                filtered_data = filtered_data[filtered_data['Chaine'].isin(kwm_values)]
            
            if order_values:
                filtered_data = filtered_data[filtered_data['Operation'].isin(order_values)]
            
            if provider_values:
                filtered_data = filtered_data[filtered_data['Controleur'].isin(provider_values)]
            
            if start_date and end_date:
                filtered_data = filtered_data[
                    (filtered_data['DATE'] >= pd.to_datetime(start_date)) &
                    (filtered_data['DATE'] <= pd.to_datetime(end_date))
                ]
            
            print("Filtered data shape:", filtered_data.shape)
            
            # Calculate metrics
            total_cnq = filtered_data['CNQ'].sum()
            avg_cnq_percentage = filtered_data['CNQ_Percentage'].mean()
            
            print("Metrics calculated:", {
                'total_cnq': total_cnq,
                'avg_cnq_percentage': avg_cnq_percentage
            })
            
            # Create gauge chart
            gauge_fig = create_gauge_chart(avg_cnq_percentage)
            
            # Create pie chart
            pie_fig = create_pie_chart(filtered_data)
            
            # Create line chart
            line_fig = create_line_chart(filtered_data)
            
            return (
                f"{total_cnq:,.2f} TND",
                f"{avg_cnq_percentage:.2f}%",
                gauge_fig,
                pie_fig,
                line_fig
            )
            
        except Exception as e:
            print(f"Error updating dashboard: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return "0 TND", "0%", {}, {}, {}

def create_gauge_chart(value):
    """Create a gauge chart for CNQ percentage"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "CNQ %", 'font': {'size': 24, 'color': 'white'}},
        gauge={
            'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#2dcecc"},
            'bgcolor': "rgba(255, 255, 255, 0.1)",
            'borderwidth': 2,
            'bordercolor': "rgba(255, 255, 255, 0.2)",
            'steps': [
                {'range': [0, 3], 'color': 'rgba(0, 255, 0, 0.1)'},
                {'range': [3, 7], 'color': 'rgba(255, 255, 0, 0.1)'},
                {'range': [7, 10], 'color': 'rgba(255, 0, 0, 0.1)'}
            ]
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        height=350
    )
    
    return fig

def create_pie_chart(data):
    """Create a pie chart showing CNQ distribution"""
    cnq_components = {
        'Retouche': data['Retouche'].sum(),
        'Rebut': data['Rebut'].sum(),
        'Penalite': data['Penalite'].sum()
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=list(cnq_components.keys()),
        values=list(cnq_components.values()),
        hole=.3,
        marker=dict(colors=['#00CCCC', '#FF9933', '#CC3366'])
    )])
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        height=350,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_line_chart(data):
    """Create a line chart showing CNQ trend"""
    # Group by date and calculate daily CNQ components
    daily_cnq = data.groupby('DATE').agg({
        'Retouche': 'sum',
        'Rebut': 'sum',
        'Penalite': 'sum',
        'CNQ': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    
    # Add traces for each component
    fig.add_trace(go.Scatter(
        x=daily_cnq['DATE'],
        y=daily_cnq['CNQ'],
        name='Total CNQ',
        line=dict(color='#2dcecc', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_cnq['DATE'],
        y=daily_cnq['Retouche'],
        name='Retouche',
        line=dict(color='#00CCCC', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_cnq['DATE'],
        y=daily_cnq['Rebut'],
        name='Rebut',
        line=dict(color='#FF9933', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_cnq['DATE'],
        y=daily_cnq['Penalite'],
        name='Pénalité',
        line=dict(color='#CC3366', width=2)
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        height=350,
        xaxis=dict(
            title="Date",
            gridcolor="rgba(255, 255, 255, 0.1)",
            showgrid=True
        ),
        yaxis=dict(
            title="CNQ (TND)",
            gridcolor="rgba(255, 255, 255, 0.1)",
            showgrid=True
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig