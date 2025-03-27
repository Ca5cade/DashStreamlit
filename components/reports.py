from dash import html, dcc
import dash_bootstrap_components as dbc
from components.filters import create_filters

def create_reports_layout(data):
    # Graph types
    graph_types = {
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
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                create_filters(data)
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Configuration du graphique"),
                    dbc.CardBody([
                        html.Label("Type de graphique"),
                        dcc.Dropdown(
                            id='graph-type-selector',
                            options=[{'label': name, 'value': graph_type} 
                                   for graph_type, name in graph_types.items()],
                            value='bar',
                            placeholder="Choisir un type de graphique",
                            className="mb-3"
                        ),
                        html.Label("Axe X"),
                        dcc.Dropdown(
                            id='x-axis-selector',
                            options=[{'label': col, 'value': col} for col in data.columns],
                            placeholder="Sélectionner X-axis",
                            className="mb-3"
                        ),
                        html.Label("Axe Y"),
                        dcc.Dropdown(
                            id='y-axis-selector',
                            options=[{'label': col, 'value': col} for col in data.columns],
                            placeholder="Sélectionner Y-axis",
                            className="mb-3"
                        ),
                        html.Label("Grouper par couleur (Optionnel)"),
                        dcc.Dropdown(
                            id='color-selector',
                            options=[{'label': col, 'value': col} for col in data.columns],
                            placeholder="Sélectionner groupement par couleur",
                            className="mb-3"
                        ),
                        dbc.Button(
                            "Ajouter graphique",
                            id="add-graph-button",
                            color="primary",
                            className="w-100 mb-3"
                        ),
                        dbc.Button(
                            "Exporter PDF",
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
                    dbc.CardHeader([
                        html.H5("Graphiques générés", className="mb-0 d-inline-block"),
                        html.Span(
                            html.I(className="fas fa-question-circle ms-2"),
                            id="graphs-help",
                            style={"cursor": "pointer"}
                        )
                    ]),
                    dbc.CardBody([
                        dbc.Alert(
                            "Ajoutez des graphiques en configurant les options à gauche et en cliquant sur 'Ajouter graphique'.",
                            id="graphs-help-text",
                            color="info",
                            dismissable=True,
                            is_open=False,
                            className="mb-3"
                        ),
                        html.Div(id="graphs-container", className="graphs-grid")
                    ])
                ])
            ], width=9)
        ])
    ])
