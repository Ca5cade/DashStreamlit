from dash import Output, Input, State, html, dcc, callback_context
import plotly.graph_objects as go
import pandas as pd
import traceback
from utils.graph_options import create_graph
from utils.pdf_generator import generate_pdf
from utils.filter_utils import apply_date_filter, apply_categorical_filter

def register_reports_callbacks(app, data):
    @app.callback(
        Output('graphs-container', 'children'),
        [Input('add-graph-button', 'n_clicks')],
        [State('graph-type-selector', 'value'),
         State('x-axis-selector', 'value'),
         State('y-axis-selector', 'value'),
         State('color-selector', 'value'),
         State('graphs-container', 'children'),
         # Add filter states to apply them to the graph
         State('filter-period', 'start_date'),
         State('filter-period', 'end_date'),
         State('filter-chain', 'value'),
         State('filter-operation', 'value'),
         State('filter-controller', 'value')]
    )
    def add_graph(n_clicks, graph_type, x_col, y_col, color_col, existing_graphs,
                 start_date, end_date, chains, operations, controllers):
        if n_clicks is None or not all([graph_type, x_col, y_col]):
            return existing_graphs or []
        
        try:
            # Apply filters to data for the graph
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
            
            # Handle date columns for better visualization
            df_for_graph = filtered_data.copy()
            
            # Convert date columns to string format for better display
            if x_col in df_for_graph.columns and pd.api.types.is_datetime64_any_dtype(df_for_graph[x_col]):
                df_for_graph[x_col] = df_for_graph[x_col].dt.strftime('%Y-%m-%d')
            
            if y_col in df_for_graph.columns and pd.api.types.is_datetime64_any_dtype(df_for_graph[y_col]):
                df_for_graph[y_col] = df_for_graph[y_col].dt.strftime('%Y-%m-%d')
            
            # For categorical columns with too many unique values, limit to top N
            if x_col in df_for_graph.columns and df_for_graph[x_col].nunique() > 20:
                top_values = df_for_graph[x_col].value_counts().nlargest(20).index
                df_for_graph = df_for_graph[df_for_graph[x_col].isin(top_values)]
            
            # Create the graph
            fig = create_graph(
                graph_type=graph_type,
                x_data=df_for_graph[x_col] if x_col in df_for_graph.columns else [],
                y_data=df_for_graph[y_col] if y_col in df_for_graph.columns else [],
                color_data=df_for_graph[color_col] if color_col in df_for_graph.columns and color_col else None,
                title=f"{y_col.replace('ID', '')} vs {x_col.replace('ID', '')}"
            )
            
            # Create graph component with controls
            new_graph = html.Div([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.H5(f"{y_col} vs {x_col}", className="d-inline me-2"),
                            html.Span(f"({graph_type})", className="text-muted small")
                        ], className="d-inline-block"),
                        html.Div([
                            html.Button(
                                html.I(className="fas fa-times"),
                                id={'type': 'remove-graph', 'index': n_clicks},
                                className="btn btn-sm btn-outline-danger",
                                title="Remove graph"
                            )
                        ], className="float-end")
                    ], className="d-flex justify-content-between align-items-center"),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=fig,
                            className="mb-0",
                            id={'type': 'report-graph', 'index': n_clicks}
                        )
                    ])
                ], className="mb-4")
            ])
            
            graphs = existing_graphs or []
            return graphs + [new_graph]
            
        except Exception as e:
            print(f"Error creating graph: {str(e)}")
            print(traceback.format_exc())
            return existing_graphs or []
    
    @app.callback(
        Output('graphs-container', 'children', allow_duplicate=True),
        [Input({'type': 'remove-graph', 'index': dash.ALL}, 'n_clicks')],
        [State('graphs-container', 'children')],
        prevent_initial_call=True
    )
    def remove_graph(n_clicks_list, existing_graphs):
        if not n_clicks_list or not any(n_clicks_list):
            return existing_graphs
            
        ctx = callback_context
        if not ctx.triggered:
            return existing_graphs
            
        # Get the id of the button that was clicked
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        index_to_remove = int(eval(button_id)['index'])
        
        # Filter out the graph with the matching index
        new_graphs = []
        for graph in existing_graphs:
            # Check if this is the graph to remove
            graph_id = None
            if 'props' in graph and 'children' in graph['props']:
                for child in graph['props']['children']:
                    if 'props' in child and 'children' in child['props']:
                        for grandchild in child['props']['children']:
                            if 'props' in grandchild and 'id' in grandchild['props']:
                                if isinstance(grandchild['props']['id'], dict) and grandchild['props']['id'].get('type') == 'report-graph':
                                    graph_id = grandchild['props']['id'].get('index')
            
            # If this is not the graph to remove, keep it
            if graph_id != index_to_remove:
                new_graphs.append(graph)
                
        return new_graphs
    
    @app.callback(
        Output('pdf-download', 'data'),
        [Input('export-pdf-button', 'n_clicks')],
        [State('graphs-container', 'children')]
    )
    def export_pdf(n_clicks, graphs):
        if n_clicks is None or not graphs:
            return None
            
        try:
            print("Starting PDF generation...")
            pdf_data = generate_pdf(graphs)
            print("PDF generation completed:", pdf_data is not None)
            return pdf_data
        except Exception as e:
            print("Error in PDF export:")
            print(traceback.format_exc())
            return None
    
    @app.callback(
        Output('graphs-help-text', 'is_open'),
        [Input('graphs-help', 'n_clicks')],
        [State('graphs-help-text', 'is_open')]
    )
    def toggle_help(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open
