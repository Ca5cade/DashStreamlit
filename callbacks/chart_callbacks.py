from dash import Output, Input, State, callback_context
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.graph_options import create_graph, create_gauge_chart
from utils.filter_utils import apply_date_filter, apply_categorical_filter

def register_chart_callbacks(app, data):
    # Callback for metric values
    @app.callback(
        [Output('total-cnq', 'children'),
         Output('cnq-percentage', 'children'),
         Output('retouche-value', 'children'),
         Output('rebut-value', 'children')],
        [Input('filter-period', 'start_date'),
         Input('filter-period', 'end_date'),
         Input('filter-chain', 'value'),
         Input('filter-operation', 'value'),
         Input('filter-controller', 'value')]
    )
    def update_metrics(start_date, end_date, chains, operations, controllers):
        # Filter data
        filtered_data = data.copy()
        
        # Apply date filter
        if start_date or end_date:
            filtered_data = apply_date_filter(filtered_data, start_date, end_date)
            
        # Apply categorical filters
        if chains and len(chains) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Chaine', chains)
            
        if operations and len(operations) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Operation', operations)
            
        if controllers and len(controllers) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Controleur', controllers)
        
        # Calculate metrics
        total_cnq = filtered_data['CNQ'].sum() if 'CNQ' in filtered_data.columns else 0
        
        # Calculate weighted average CNQ percentage
        if 'CNQ_Percentage' in filtered_data.columns and 'Quantite' in filtered_data.columns:
            cnq_percentage = (filtered_data['CNQ'] / filtered_data['Quantite'].replace(0, np.nan)).mean() * 100
        else:
            cnq_percentage = filtered_data['CNQ_Percentage'].mean() if 'CNQ_Percentage' in filtered_data.columns else 0
        
        retouche = filtered_data['Retouche'].sum() if 'Retouche' in filtered_data.columns else 0
        rebut = filtered_data['Rebut'].sum() if 'Rebut' in filtered_data.columns else 0
        
        # Format values
        formatted_cnq = f"{total_cnq:,.0f} €"
        formatted_cnq_percentage = f"{cnq_percentage:.2f}%"
        formatted_retouche = f"{retouche:,.0f} €"
        formatted_rebut = f"{rebut:,.0f} €"
        
        return formatted_cnq, formatted_cnq_percentage, formatted_retouche, formatted_rebut
    
    # Callback for gauge chart
    @app.callback(
        Output('gauge-chart', 'figure'),
        [Input('filter-period', 'start_date'),
         Input('filter-period', 'end_date'),
         Input('filter-chain', 'value'),
         Input('filter-operation', 'value'),
         Input('filter-controller', 'value')]
    )
    def update_gauge_chart(start_date, end_date, chains, operations, controllers):
        # Filter data
        filtered_data = data.copy()
        
        # Apply date filter
        if start_date or end_date:
            filtered_data = apply_date_filter(filtered_data, start_date, end_date)
            
        # Apply categorical filters
        if chains and len(chains) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Chaine', chains)
            
        if operations and len(operations) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Operation', operations)
            
        if controllers and len(controllers) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Controleur', controllers)
        
        # Calculate metrics for gauge
        total_cnq = filtered_data['CNQ'].sum() if 'CNQ' in filtered_data.columns else 0
        
        # Set a target value or use a percentage of total production value
        if 'Quantite' in filtered_data.columns:
            total_value = filtered_data['Quantite'].sum() * 100  # Assume 100€ per unit
            max_acceptable_cnq = total_value * 0.05  # 5% of total value as maximum acceptable CNQ
        else:
            # Fallback to a reasonable multiple of current CNQ
            max_acceptable_cnq = max(10000, total_cnq * 2)
        
        # Create gauge chart
        fig = create_gauge_chart(
            value=total_cnq,
            max_val=max_acceptable_cnq,
            title="CNQ Cumulé"
        )
        
        return fig
    
    # Callback for pie chart
    @app.callback(
        Output('pie-chart', 'figure'),
        [Input('filter-period', 'start_date'),
         Input('filter-period', 'end_date'),
         Input('filter-chain', 'value'),
         Input('filter-operation', 'value'),
         Input('filter-controller', 'value')]
    )
    def update_pie_chart(start_date, end_date, chains, operations, controllers):
        # Filter data
        filtered_data = data.copy()
        
        # Apply date filter
        if start_date or end_date:
            filtered_data = apply_date_filter(filtered_data, start_date, end_date)
            
        # Apply categorical filters
        if chains and len(chains) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Chaine', chains)
            
        if operations and len(operations) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Operation', operations)
            
        if controllers and len(controllers) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Controleur', controllers)
        
        # Calculate components for pie chart
        retouche = filtered_data['Retouche'].sum() if 'Retouche' in filtered_data.columns else 0
        rebut = filtered_data['Rebut'].sum() if 'Rebut' in filtered_data.columns else 0
        penalite = filtered_data['Penalite'].sum() if 'Penalite' in filtered_data.columns else 0
        
        # Create pie chart data
        labels = ['Retouche', 'Rebut', 'Pénalité']
        values = [retouche, rebut, penalite]
        
        # Check if we have non-zero values
        if sum(values) == 0:
            # Create empty pie chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="Pas de données disponibles",
                showarrow=False,
                font=dict(size=18)
            )
        else:
            # Create pie chart
            fig = px.pie(
                names=labels,
                values=values,
                title="Répartition CNQ",
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            
            # Add percentage and value in hover
            fig.update_traces(
                hoverinfo='label+percent+value',
                textinfo='percent+value',
                textposition='inside'
            )
        
        # Update layout
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=50, b=20),
            height=350
        )
        
        return fig
    
    # Callback for line chart - trend over time
    @app.callback(
        Output('line-chart', 'figure'),
        [Input('filter-period', 'start_date'),
         Input('filter-period', 'end_date'),
         Input('filter-chain', 'value'),
         Input('filter-operation', 'value'),
         Input('filter-controller', 'value'),
         Input('line-day-btn', 'n_clicks'),
         Input('line-week-btn', 'n_clicks'),
         Input('line-month-btn', 'n_clicks')]
    )
    def update_line_chart(start_date, end_date, chains, operations, controllers, 
                          day_clicks, week_clicks, month_clicks):
        # Determine which time period button was clicked
        ctx = callback_context
        if not ctx.triggered:
            time_period = 'month'  # Default
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'line-day-btn':
                time_period = 'day'
            elif button_id == 'line-week-btn':
                time_period = 'week'
            else:
                time_period = 'month'
        
        # Filter data
        filtered_data = data.copy()
        
        # Apply date filter
        if start_date or end_date:
            filtered_data = apply_date_filter(filtered_data, start_date, end_date)
            
        # Apply categorical filters
        if chains and len(chains) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Chaine', chains)
            
        if operations and len(operations) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Operation', operations)
            
        if controllers and len(controllers) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Controleur', controllers)
        
        # Check if we have date column
        if 'DATE' not in filtered_data.columns or filtered_data.empty:
            # Create empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="Pas de données disponibles pour l'historique",
                showarrow=False,
                font=dict(size=18)
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=50, b=20),
                height=350
            )
            return fig
        
        # Group by time period
        if time_period == 'day':
            # Daily trend
            filtered_data['TimePeriod'] = filtered_data['DATE'].dt.date
            freq = 'D'
        elif time_period == 'week':
            # Weekly trend
            filtered_data['TimePeriod'] = filtered_data['DATE'].dt.to_period('W').apply(lambda x: x.start_time)
            freq = 'W'
        else:
            # Monthly trend
            filtered_data['TimePeriod'] = filtered_data['DATE'].dt.to_period('M').apply(lambda x: x.start_time)
            freq = 'M'
        
        # Aggregate data by time period
        trend_data = filtered_data.groupby('TimePeriod').agg({
            'CNQ': 'sum',
            'Retouche': 'sum',
            'Rebut': 'sum',
            'Penalite': 'sum'
        }).reset_index()
        
        # Create time series chart
        fig = go.Figure()
        
        # Add total CNQ line
        fig.add_trace(go.Scatter(
            x=trend_data['TimePeriod'],
            y=trend_data['CNQ'],
            name='CNQ Total',
            line=dict(color='#2dcecc', width=3),
            mode='lines+markers'
        ))
        
        # Add component lines
        fig.add_trace(go.Scatter(
            x=trend_data['TimePeriod'],
            y=trend_data['Retouche'],
            name='Retouche',
            line=dict(color='#8c67ef', width=2),
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_data['TimePeriod'],
            y=trend_data['Rebut'],
            name='Rebut',
            line=dict(color='#f2c85b', width=2),
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_data['TimePeriod'],
            y=trend_data['Penalite'],
            name='Pénalité',
            line=dict(color='#e97254', width=2),
            mode='lines+markers'
        ))
        
        # Add moving average for CNQ
        window_size = 3 if len(trend_data) >= 3 else len(trend_data)
        if window_size > 0:
            trend_data['CNQ_MA'] = trend_data['CNQ'].rolling(window=window_size, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=trend_data['TimePeriod'],
                y=trend_data['CNQ_MA'],
                name=f'CNQ (Moyenne mobile sur {window_size})',
                line=dict(color='white', width=2, dash='dot'),
                mode='lines'
            ))
        
        # Update layout
        fig.update_layout(
            title=f"Évolution CNQ par {time_period}",
            xaxis_title="Période",
            yaxis_title="Valeur (€)",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=50, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=350,
            hovermode="x unified"
        )
        
        # Add grid lines
        fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(255,255,255,0.1)')
        
        return fig
    
    # Callback for top chart (by Chain, Operation, Controller)
    @app.callback(
        Output('top-chart', 'figure'),
        [Input('filter-period', 'start_date'),
         Input('filter-period', 'end_date'),
         Input('filter-chain', 'value'),
         Input('filter-operation', 'value'),
         Input('filter-controller', 'value'),
         Input('top-chain-btn', 'n_clicks'),
         Input('top-operation-btn', 'n_clicks'),
         Input('top-controller-btn', 'n_clicks')]
    )
    def update_top_chart(start_date, end_date, chains, operations, controllers,
                         chain_clicks, operation_clicks, controller_clicks):
        # Determine which category button was clicked
        ctx = callback_context
        if not ctx.triggered:
            category = 'Chaine'  # Default
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'top-chain-btn':
                category = 'Chaine'
            elif button_id == 'top-operation-btn':
                category = 'Operation'
            else:
                category = 'Controleur'
        
        # Filter data
        filtered_data = data.copy()
        
        # Apply date filter
        if start_date or end_date:
            filtered_data = apply_date_filter(filtered_data, start_date, end_date)
            
        # Apply categorical filters, but not for the category we're showing
        if category != 'Chaine' and chains and len(chains) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Chaine', chains)
            
        if category != 'Operation' and operations and len(operations) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Operation', operations)
            
        if category != 'Controleur' and controllers and len(controllers) > 0:
            filtered_data = apply_categorical_filter(filtered_data, 'Controleur', controllers)
        
        # Check if category exists in data
        if category not in filtered_data.columns or filtered_data.empty:
            # Create empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text=f"Pas de données disponibles pour {category}",
                showarrow=False,
                font=dict(size=18)
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=50, b=20),
                height=350
            )
            return fig
        
        # Group by category and calculate metrics
        top_data = filtered_data.groupby(category).agg({
            'CNQ': 'sum',
            'CNQ_Percentage': 'mean',
            'Retouche': 'sum',
            'Rebut': 'sum',
            'Penalite': 'sum',
            'Quantite': 'sum'
        }).reset_index()
        
        # Sort by CNQ descending and take top 10
        top_data = top_data.sort_values('CNQ', ascending=False).head(10)
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        # Add CNQ bars
        fig.add_trace(go.Bar(
            y=top_data[category],
            x=top_data['CNQ'],
            name='CNQ Total',
            orientation='h',
            marker=dict(color='#2dcecc')
        ))
        
        # Add component bars in a grouped format
        fig.add_trace(go.Bar(
            y=top_data[category],
            x=top_data['Retouche'],
            name='Retouche',
            orientation='h',
            marker=dict(color='#8c67ef')
        ))
        
        fig.add_trace(go.Bar(
            y=top_data[category],
            x=top_data['Rebut'],
            name='Rebut',
            orientation='h',
            marker=dict(color='#f2c85b')
        ))
        
        fig.add_trace(go.Bar(
            y=top_data[category],
            x=top_data['Penalite'],
            name='Pénalité',
            orientation='h',
            marker=dict(color='#e97254')
        ))
        
        # Update layout
        category_names = {
            'Chaine': 'Chaînes',
            'Operation': 'Opérations',
            'Controleur': 'Contrôleurs'
        }
        
        fig.update_layout(
            title=f"Top 10 {category_names.get(category, category)} par CNQ",
            xaxis_title="Valeur (€)",
            yaxis_title=category,
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=50, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=350,
            barmode='group'
        )
        
        # Add grid lines
        fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(255,255,255,0.1)')
        
        # Reverse y-axis to show highest value at top
        fig.update_layout(yaxis=dict(autorange="reversed"))
        
        return fig
    
    # Update button styles based on selection
    @app.callback(
        [Output('line-day-btn', 'outline'),
         Output('line-week-btn', 'outline'),
         Output('line-month-btn', 'outline')],
        [Input('line-day-btn', 'n_clicks'),
         Input('line-week-btn', 'n_clicks'),
         Input('line-month-btn', 'n_clicks')]
    )
    def update_line_buttons(day_clicks, week_clicks, month_clicks):
        ctx = callback_context
        if not ctx.triggered:
            # Default is month selected
            return True, True, False
            
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'line-day-btn':
            return False, True, True
        elif button_id == 'line-week-btn':
            return True, False, True
        else:  # month button
            return True, True, False
    
    # Update button styles for top chart categories
    @app.callback(
        [Output('top-chain-btn', 'outline'),
         Output('top-operation-btn', 'outline'),
         Output('top-controller-btn', 'outline')],
        [Input('top-chain-btn', 'n_clicks'),
         Input('top-operation-btn', 'n_clicks'),
         Input('top-controller-btn', 'n_clicks')]
    )
    def update_top_buttons(chain_clicks, operation_clicks, controller_clicks):
        ctx = callback_context
        if not ctx.triggered:
            # Default is chain selected
            return False, True, True
            
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'top-chain-btn':
            return False, True, True
        elif button_id == 'top-operation-btn':
            return True, False, True
        else:  # controller button
            return True, True, False
