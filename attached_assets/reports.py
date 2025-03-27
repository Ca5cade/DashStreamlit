from dash import html, dcc
import dash_bootstrap_components as dbc
from utils.graph_options import GRAPH_TYPES

def create_reports_layout(data):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Graph Configuration"),
                    dbc.CardBody([
                        html.Label("Select Graph Type"),
                        dcc.Dropdown(
                            id='graph-type-selector',
                            options=[{'label': name, 'value': graph_type} 
                                   for graph_type, name in GRAPH_TYPES.items()],
                            placeholder="Choose a graph type",
                            className="mb-3"
                        ),
                        html.Label("X-Axis"),
                        dcc.Dropdown(
                            id='x-axis-selector',
                            options=[{'label': col, 'value': col} for col in data.columns],
                            placeholder="Select X-axis",
                            className="mb-3"
                        ),
                        html.Label("Y-Axis"),
                        dcc.Dropdown(
                            id='y-axis-selector',
                            options=[{'label': col, 'value': col} for col in data.columns],
                            placeholder="Select Y-axis",
                            className="mb-3"
                        ),
                        html.Label("Color By (Optional)"),
                        dcc.Dropdown(
                            id='color-selector',
                            options=[{'label': col, 'value': col} for col in data.columns],
                            placeholder="Select color grouping",
                            className="mb-3"
                        ),
                        dbc.Button(
                            "Add Graph",
                            id="add-graph-button",
                            color="primary",
                            className="w-100 mb-3"
                        ),
                        dbc.Button(
                            "Export PDF",
                            id="export-pdf-button",
                            color="success",
                            className="w-100"
                        ),
                        dcc.Download(id="pdf-download")
                    ])
                ], className="mb-4")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Generated Graphs"),
                    dbc.CardBody([
                        html.Div(id="graphs-container", className="graphs-grid")
                    ])
                ])
            ], width=9)
        ])
    ])

