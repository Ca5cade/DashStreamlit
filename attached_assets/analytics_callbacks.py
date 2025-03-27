from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_ag_grid import AgGrid
import plotly.express as px
import pandas as pd
import html

def register_analytics_callbacks(app, data):
    @app.callback(
        [Output('analytics-table', 'children'),
         Output('analytics-summary', 'children'),
         Output('analytics-chart', 'figure')],
        [Input('analytics-apply', 'n_clicks')],
        [State('analytics-date-range', 'start_date'),
         State('analytics-date-range', 'end_date'),
         State('analytics-chain', 'value'),
         State('analytics-operation', 'value'),
         State('analytics-metrics', 'value'),
         State('analytics-groupby', 'value')]
    )
    def update_analytics(n_clicks, start_date, end_date, chains, operations, metrics, groupby):
        if n_clicks is None:
            raise PreventUpdate
            
        try:
            # Filter data
            filtered_data = data.copy()
            
            if start_date and end_date:
                filtered_data = filtered_data[
                    (filtered_data['DATE'] >= pd.to_datetime(start_date)) &
                    (filtered_data['DATE'] <= pd.to_datetime(end_date))
                ]
            
            if chains:
                filtered_data = filtered_data[filtered_data['Chaine'].isin(chains)]
            
            if operations:
                filtered_data = filtered_data[filtered_data['Operation'].isin(operations)]
            
            # Group data if groupby is specified
            if groupby:
                # Prepare metrics for aggregation
                agg_dict = {}
                if metrics:
                    for metric in metrics:
                        agg_dict[metric] = 'sum'
                
                # Group the data
                result_data = filtered_data.groupby(groupby).agg(agg_dict).reset_index()
            else:
                # Use filtered data as is
                result_data = filtered_data
            
            # Create table
            table = AgGrid(
                rowData=result_data.to_dict('records'),
                columnDefs=[{"field": i} for i in result_data.columns],
                defaultColDef={
                    "resizable": True,
                    "sortable": True,
                    "filter": True
                },
                dashGridOptions={"pagination": True},
                className="ag-theme-alpine-dark"
            )
            
            # Create summary
            summary_stats = []
            if metrics:
                for metric in metrics:
                    summary_stats.append(
                        html.Div([
                            html.Strong(f"{metric}: "),
                            f"Total: {result_data[metric].sum():,.2f}, ",
                            f"Average: {result_data[metric].mean():,.2f}, ",
                            f"Max: {result_data[metric].max():,.2f}"
                        ], className="mb-2")
                    )
            
            # Create visualization
            if groupby and metrics and len(groupby) <= 2:
                if len(groupby) == 1:
                    fig = px.bar(
                        result_data,
                        x=groupby[0],
                        y=metrics,
                        title="Metrics by " + groupby[0]
                    )
                else:
                    fig = px.bar(
                        result_data,
                        x=groupby[0],
                        y=metrics[0] if len(metrics) > 0 else None,
                        color=groupby[1],
                        title=f"{metrics[0]} by {groupby[0]} and {groupby[1]}"
                    )
            else:
                fig = px.scatter(
                    result_data,
                    title="Data Distribution"
                )
            
            # Update layout
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            return table, summary_stats, fig
            
        except Exception as e:
            print(f"Error in analytics callback: {str(e)}")
            return None, html.Div("Error processing data"), {}
    
    @app.callback(
        Output('analytics-export', 'href'),
        [Input('analytics-apply', 'n_clicks')],
        [State('analytics-date-range', 'start_date'),
         State('analytics-date-range', 'end_date'),
         State('analytics-chain', 'value'),
         State('analytics-operation', 'value'),
         State('analytics-metrics', 'value'),
         State('analytics-groupby', 'value')]
    )
    def export_data(n_clicks, start_date, end_date, chains, operations, metrics, groupby):
        if n_clicks is None:
            raise PreventUpdate
            
        try:
            # Filter and process data (similar to above)
            filtered_data = data.copy()
            
            if start_date and end_date:
                filtered_data = filtered_data[
                    (filtered_data['DATE'] >= pd.to_datetime(start_date)) &
                    (filtered_data['DATE'] <= pd.to_datetime(end_date))
                ]
            
            if chains:
                filtered_data = filtered_data[filtered_data['Chaine'].isin(chains)]
            
            if operations:
                filtered_data = filtered_data[filtered_data['Operation'].isin(operations)]
            
            # Export to CSV
            csv_string = filtered_data.to_csv(index=False, encoding='utf-8')
            csv_string = "data:text/csv;charset=utf-8," + csv_string
            
            return csv_string
            
        except Exception as e:
            print(f"Error in export callback: {str(e)}")
            return None