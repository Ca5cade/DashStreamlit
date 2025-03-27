from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_ag_grid import AgGrid
from components.filters import create_filters

def create_analytics_layout(data):
    # Define important columns to show in filters
    important_columns = [
        'Chaine', 'Operation', 'Controleur', 'DATE', 'Quantite',
        'CNQ', 'CNQ_Percentage', 'Retouche', 'Rebut', 'Penalite'
    ]
    
    # Get available columns from data
    available_columns = [col for col in important_columns if col in data.columns]
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                create_filters(data)
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Extraction de données", className="mb-0"),
                        html.P("Extrayez et analysez les données à l'aide de filtres", className="text-muted small mb-0")
                    ]),
                    dbc.CardBody([
                        # Metrics Selection
                        dbc.Row([
                            dbc.Col([
                                html.Label("Métriques", className="mb-2"),
                                dcc.Dropdown(
                                    id='analytics-metrics',
                                    options=[
                                        {'label': col, 'value': col}
                                        for col in ['CNQ', 'CNQ_Percentage', 'Retouche', 'Rebut', 'Penalite']
                                        if col in data.columns
                                    ],
                                    multi=True,
                                    value=['CNQ', 'CNQ_Percentage'] if 'CNQ' in data.columns else [],
                                    placeholder="Sélectionner les métriques",
                                    className="mb-3"
                                )
                            ], width=8),
                            dbc.Col([
                                html.Label("Type de graphique", className="mb-2"),
                                dcc.Dropdown(
                                    id='analytics-chart-type',
                                    options=[
                                        {'label': 'Bar Chart', 'value': 'bar'},
                                        {'label': 'Line Chart', 'value': 'line'},
                                        {'label': 'Pie Chart', 'value': 'pie'},
                                        {'label': 'Treemap', 'value': 'treemap'},
                                    ],
                                    value='bar',
                                    placeholder="Sélectionner type de graphique",
                                    className="mb-3"
                                )
                            ], width=4)
                        ]),
                        
                        # Group By Selection
                        dbc.Row([
                            dbc.Col([
                                html.Label("Regrouper par", className="mb-2"),
                                dcc.Dropdown(
                                    id='analytics-groupby',
                                    options=[
                                        {'label': 'Chaîne', 'value': 'Chaine'},
                                        {'label': 'Opération', 'value': 'Operation'},
                                        {'label': 'Contrôleur', 'value': 'Controleur'},
                                        {'label': 'Jour', 'value': 'DATE'},
                                        {'label': 'Mois', 'value': 'Month'},
                                        {'label': 'Année', 'value': 'Year'}
                                    ],
                                    multi=True,
                                    value=['Chaine'] if 'Chaine' in data.columns else [],
                                    placeholder="Sélectionner le regroupement",
                                    className="mb-3"
                                )
                            ], width=8),
                            dbc.Col([
                                html.Label("Limiter résultats", className="mb-2"),
                                dcc.Dropdown(
                                    id='analytics-limit',
                                    options=[
                                        {'label': 'Top 5', 'value': 5},
                                        {'label': 'Top 10', 'value': 10},
                                        {'label': 'Top 20', 'value': 20},
                                        {'label': 'Tous', 'value': 0}
                                    ],
                                    value=10,
                                    placeholder="Limiter les résultats",
                                    className="mb-3"
                                )
                            ], width=4)
                        ]),
                        
                        # Action Buttons
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "Appliquer l'analyse",
                                    id="analytics-apply",
                                    color="primary",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    "Exporter les données",
                                    id="analytics-export",
                                    color="success",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    "Réinitialiser",
                                    id="analytics-reset",
                                    color="danger",
                                    outline=True
                                )
                            ])
                        ])
                    ])
                ], className="mb-4")
            ], width=12)
        ]),
        
        # Results Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Résultats", className="mb-0"),
                        html.Div(id="results-summary", className="text-muted small")
                    ]),
                    dbc.CardBody([
                        # Tabs for different views
                        dbc.Tabs([
                            dbc.Tab([
                                # Loading spinner
                                dbc.Spinner(
                                    children=[
                                        # Visualization
                                        dcc.Graph(id='analytics-chart', className="mb-4"),
                                        
                                        # Summary statistics
                                        html.Div(id='analytics-summary', className="mb-4")
                                    ],
                                    color="primary",
                                    type="border",
                                    fullscreen=False
                                )
                            ], label="Graphique", tab_id="tab-chart"),
                            dbc.Tab([
                                # Loading spinner
                                dbc.Spinner(
                                    children=[
                                        # Data table
                                        html.Div(id='analytics-table', className="mb-4"),
                                    ],
                                    color="primary",
                                    type="border",
                                    fullscreen=False
                                )
                            ], label="Tableau de données", tab_id="tab-table"),
                        ], id="analytics-tabs", active_tab="tab-chart")
                    ])
                ])
            ])
        ]),
        
        # Download Component
        dcc.Download(id="analytics-download")
    ])
