from dash import Output, Input, State, html, dcc
import dash_bootstrap_components as dbc
from dash_ag_grid import AgGrid
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.filter_utils import apply_date_filter, apply_categorical_filter, apply_numerical_filter, calculate_aggregations
import base64
import io

def register_analytics_callbacks(app, data):
    @app.callback(
        [Output('analytics-table', 'children'),
         Output('analytics-chart', 'figure'),
         Output('analytics-summary', 'children'),
         Output('results-summary', 'children')],
        [Input('analytics-apply', 'n_clicks')],
        [State('filter-period', 'start_date'),
         State('filter-period', 'end_date'),
         State('filter-chain', 'value'),
         State('filter-operation', 'value'),
         State('filter-controller', 'value'),
         State('filter-cnq-min', 'value'),
         State('filter-cnq-max', 'value'),
         State('filter-cnq-pct-min', 'value'),
         State('filter-cnq-pct-max', 'value'),
         State('analytics-metrics', 'value'),
         State('analytics-groupby', 'value'),
         State('analytics-chart-type', 'value'),
         State('analytics-limit', 'value')]
    )
    def update_analytics(n_clicks, start_date, end_date, chains, operations, controllers, 
                        cnq_min, cnq_max, cnq_pct_min, cnq_pct_max, metrics, group_by, chart_type, limit):
        if n_clicks is None:
            # Initial empty state
            fig = go.Figure()
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            return html.Div(), fig, html.Div(), html.Div("Utilisez les filtres et cliquez sur 'Appliquer l'analyse'")
            
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
            
        # Apply numerical filters
        if cnq_min is not None or cnq_max is not None:
            filtered_data = apply_numerical_filter(filtered_data, 'CNQ', cnq_min, cnq_max)
            
        if cnq_pct_min is not None or cnq_pct_max is not None:
            filtered_data = apply_numerical_filter(filtered_data, 'CNQ_Percentage', cnq_pct_min, cnq_pct_max)
            
        # Handle empty data
        if filtered_data.empty:
            fig = go.Figure()
            fig.update_layout(
                title="No data matches the selected filters",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            return html.Div("No data matches the selected filters"), fig, html.Div(), html.Div("No data matches the selected filters")
            
        # Default metrics if none selected
        if not metrics or len(metrics) == 0:
            metrics = ['CNQ'] if 'CNQ' in filtered_data.columns else filtered_data.select_dtypes(include=[np.number]).columns[:1].tolist()
            
        # Default group by if none selected
        if not group_by or len(group_by) == 0:
            group_by = ['Chaine'] if 'Chaine' in filtered_data.columns else filtered_data.select_dtypes(exclude=[np.number]).columns[:1].tolist()
            
        # Calculate aggregations
        aggregated_data = calculate_aggregations(filtered_data, group_by, metrics)
        
        # Sort by the first metric in descending order
        sort_by = metrics[0] if metrics else None
        if sort_by and sort_by in aggregated_data.columns:
            aggregated_data = aggregated_data.sort_values(by=sort_by, ascending=False)
        
        # Apply limit if specified
        if limit and limit > 0:
            aggregated_data = aggregated_data.head(limit)
            
        # Create chart
        if chart_type == 'bar':
            if len(group_by) == 1:
                # Simple bar chart
                fig = px.bar(
                    aggregated_data, 
                    x=group_by[0], 
                    y=metrics,
                    title=f'{", ".join(metrics)} by {group_by[0]}',
                    barmode='group',
                    template="plotly_dark"
                )
            else:
                # Grouped bar chart
                fig = px.bar(
                    aggregated_data,
                    x=group_by[0],
                    y=metrics[0] if metrics else None,
                    color=group_by[1] if len(group_by) > 1 else None,
                    title=f'{metrics[0] if metrics else ""} by {", ".join(group_by)}',
                    barmode='group',
                    template="plotly_dark"
                )
        elif chart_type == 'line':
            if len(group_by) == 1:
                fig = px.line(
                    aggregated_data,
                    x=group_by[0],
                    y=metrics,
                    title=f'{", ".join(metrics)} by {group_by[0]}',
                    template="plotly_dark",
                    markers=True
                )
            else:
                fig = px.line(
                    aggregated_data,
                    x=group_by[0],
                    y=metrics[0] if metrics else None,
                    color=group_by[1] if len(group_by) > 1 else None,
                    title=f'{metrics[0] if metrics else ""} by {", ".join(group_by)}',
                    template="plotly_dark",
                    markers=True
                )
        elif chart_type == 'pie':
            fig = px.pie(
                aggregated_data,
                names=group_by[0],
                values=metrics[0] if metrics else None,
                title=f'{metrics[0] if metrics else ""} by {group_by[0]}',
                template="plotly_dark"
            )
        elif chart_type == 'treemap':
            path = group_by
            fig = px.treemap(
                aggregated_data,
                path=path,
                values=metrics[0] if metrics else None,
                title=f'{metrics[0] if metrics else ""} by {", ".join(group_by)}',
                template="plotly_dark"
            )
        else:
            # Default to bar chart
            fig = px.bar(
                aggregated_data,
                x=group_by[0],
                y=metrics,
                title=f'{", ".join(metrics)} by {group_by[0]}',
                barmode='group',
                template="plotly_dark"
            )
            
        # Improve chart appearance
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=80, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Create data table
        table = dbc.Table.from_dataframe(
            aggregated_data,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            className="data-table"
        )
        
        # Create summary statistics
        summary_rows = []
        
        for metric in metrics:
            if metric in filtered_data.columns:
                # Calculate statistics
                total = filtered_data[metric].sum()
                mean = filtered_data[metric].mean()
                median = filtered_data[metric].median()
                min_val = filtered_data[metric].min()
                max_val = filtered_data[metric].max()
                
                # Add to summary
                summary_rows.append(
                    html.Tr([
                        html.Td(metric, className="fw-bold"),
                        html.Td(f"{total:,.2f}", className="text-end"),
                        html.Td(f"{mean:,.2f}", className="text-end"),
                        html.Td(f"{median:,.2f}", className="text-end"),
                        html.Td(f"{min_val:,.2f}", className="text-end"),
                        html.Td(f"{max_val:,.2f}", className="text-end")
                    ])
                )
        
        summary = html.Div([
            html.H5("Statistiques des métriques"),
            html.Table(
                [
                    html.Thead(
                        html.Tr([
                            html.Th("Métrique"),
                            html.Th("Total", className="text-end"),
                            html.Th("Moyenne", className="text-end"),
                            html.Th("Médiane", className="text-end"),
                            html.Th("Min", className="text-end"),
                            html.Th("Max", className="text-end")
                        ])
                    ),
                    html.Tbody(summary_rows)
                ],
                className="table table-sm table-striped table-bordered"
            )
        ])
        
        # Results summary
        results_text = f"Affichage de {len(aggregated_data)} résultats sur {len(filtered_data)} enregistrements filtrés"
        
        return table, fig, summary, results_text
        
    @app.callback(
        Output('analytics-download', 'data'),
        [Input('analytics-export', 'n_clicks')],
        [State('filter-period', 'start_date'),
         State('filter-period', 'end_date'),
         State('filter-chain', 'value'),
         State('filter-operation', 'value'),
         State('filter-controller', 'value'),
         State('filter-cnq-min', 'value'),
         State('filter-cnq-max', 'value'),
         State('filter-cnq-pct-min', 'value'),
         State('filter-cnq-pct-max', 'value'),
         State('analytics-metrics', 'value'),
         State('analytics-groupby', 'value'),
         State('analytics-limit', 'value')]
    )
    def export_data(n_clicks, start_date, end_date, chains, operations, controllers, 
                   cnq_min, cnq_max, cnq_pct_min, cnq_pct_max, metrics, group_by, limit):
        if n_clicks is None:
            return None
            
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
            
        # Apply numerical filters
        if cnq_min is not None or cnq_max is not None:
            filtered_data = apply_numerical_filter(filtered_data, 'CNQ', cnq_min, cnq_max)
            
        if cnq_pct_min is not None or cnq_pct_max is not None:
            filtered_data = apply_numerical_filter(filtered_data, 'CNQ_Percentage', cnq_pct_min, cnq_pct_max)
            
        # Default metrics if none selected
        if not metrics or len(metrics) == 0:
            metrics = ['CNQ'] if 'CNQ' in filtered_data.columns else filtered_data.select_dtypes(include=[np.number]).columns[:1].tolist()
            
        # Default group by if none selected
        if not group_by or len(group_by) == 0:
            group_by = ['Chaine'] if 'Chaine' in filtered_data.columns else filtered_data.select_dtypes(exclude=[np.number]).columns[:1].tolist()
            
        # Calculate aggregations if group_by is specified
        if group_by and len(group_by) > 0:
            export_data = calculate_aggregations(filtered_data, group_by, metrics)
            
            # Sort by the first metric in descending order
            sort_by = metrics[0] if metrics else None
            if sort_by and sort_by in export_data.columns:
                export_data = export_data.sort_values(by=sort_by, ascending=False)
            
            # Apply limit if specified
            if limit and limit > 0:
                export_data = export_data.head(limit)
        else:
            # Export raw filtered data
            export_data = filtered_data
            
        # Convert to CSV
        csv_string = export_data.to_csv(index=False, encoding='utf-8')
        
        # Return download data
        return dict(
            content=csv_string,
            filename='analytics_export.csv',
            type='text/csv'
        )
        
    @app.callback(
        [Output('analytics-metrics', 'options'),
         Output('analytics-groupby', 'options')],
        [Input('filter-period', 'start_date'),
         Input('filter-period', 'end_date'),
         Input('filter-chain', 'value'),
         Input('filter-operation', 'value'),
         Input('filter-controller', 'value')]
    )
    def update_dropdown_options(start_date, end_date, chains, operations, controllers):
        # Filter data to get relevant options
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
            
        # Get numeric columns for metrics
        metric_columns = filtered_data.select_dtypes(include=[np.number]).columns.tolist()
        metric_options = [{'label': col, 'value': col} for col in metric_columns]
        
        # Get categorical columns for groupby
        # Include date columns
        categorical_columns = filtered_data.select_dtypes(exclude=[np.number]).columns.tolist()
        date_column = 'DATE'
        if date_column in filtered_data.columns and date_column not in categorical_columns:
            categorical_columns.append(date_column)
            
        # Add month and year options
        groupby_options = [
            {'label': 'Chaîne', 'value': 'Chaine'},
            {'label': 'Opération', 'value': 'Operation'},
            {'label': 'Contrôleur', 'value': 'Controleur'},
            {'label': 'Jour', 'value': 'DATE'},
            {'label': 'Mois', 'value': 'Month'},
            {'label': 'Année', 'value': 'Year'}
        ]
        
        return metric_options, groupby_options
