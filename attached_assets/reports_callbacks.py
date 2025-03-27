from dash import Output, Input, State, html, dcc
import plotly.graph_objects as go
import pandas as pd
import traceback

# Assume create_graph and generate_pdf are defined elsewhere
from utils.graph_options import create_graph
from utils.pdf_generator import generate_pdf

def register_reports_callbacks(app, data):
    @app.callback(
        Output('graphs-container', 'children'),
        [Input('add-graph-button', 'n_clicks')],
        [State('graph-type-selector', 'value'),
         State('x-axis-selector', 'value'),
         State('y-axis-selector', 'value'),
         State('color-selector', 'value'),
         State('graphs-container', 'children')]
    )
    def add_graph(n_clicks, graph_type, x_col, y_col, color_col, existing_graphs):
        if n_clicks is None or not all([graph_type, x_col, y_col]):
            return existing_graphs or []
        
        try:
            # Handle date columns for better visualization
            df_for_graph = data.copy()
            
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
                color_data=df_for_graph[color_col] if color_col in df_for_graph.columns else None,
                title=f"{y_col.replace('ID', '')} vs {x_col.replace('ID', '')}"
            )
            
            new_graph = html.Div([
                dcc.Graph(
                    figure=fig,
                    className="mb-4",
                    id={'type': 'report-graph', 'index': n_clicks}
                )
            ])
            
            graphs = existing_graphs or []
            return graphs + [new_graph]
            
        except Exception as e:
            print(f"Error creating graph: {str(e)}")
            return existing_graphs or []
    
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

