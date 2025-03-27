from dash import html, dcc
import dash_bootstrap_components as dbc
from components.metrics import create_metrics

def create_charts():
    return html.Div([
        # Metrics row
        create_metrics(),
        
        # Charts row
        dbc.Row([
            # Gauge chart for CNQ Cumulé
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("CNQ Cumulé (en chiffre et en %)", className="mb-0 text-center"),
                    ], className="text-center"),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-gauge",
                            type="circle",
                            children=[
                                dcc.Graph(
                                    id="gauge-chart",
                                    className="chart-container",
                                    config={'displayModeBar': False},
                                    style={'height': '350px'}
                                )
                            ]
                        )
                    ], className="chart-body-fixed")
                ], className="chart-card"),
                width=6
            ),
            
            # Pie chart for Répartition CNQ
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Répartition CNQ (retouche, rebut, pénalité)", className="mb-0 text-center"),
                    ], className="text-center"),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-pie",
                            type="circle",
                            children=[
                                dcc.Graph(
                                    id="pie-chart",
                                    className="chart-container",
                                    config={'displayModeBar': False},
                                    style={'height': '350px'}
                                )
                            ]
                        )
                    ], className="chart-body-fixed")
                ], className="chart-card"),
                width=6
            )
        ], className="mb-4"),
        
        dbc.Row([
            # Line chart for Historique CNQ
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Courbe tendance de l'historique CNQ", className="mb-0 text-center"),
                        dbc.ButtonGroup([
                            dbc.Button("Jour", id="line-day-btn", color="primary", outline=True, size="sm", n_clicks=0, className="mx-1"),
                            dbc.Button("Semaine", id="line-week-btn", color="primary", outline=True, size="sm", n_clicks=0, className="mx-1"),
                            dbc.Button("Mois", id="line-month-btn", color="primary", outline=True, size="sm", n_clicks=1, className="mx-1")
                        ], className="float-end")
                    ], className="d-flex justify-content-between align-items-center"),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-line",
                            type="circle",
                            children=[
                                dcc.Graph(
                                    id="line-chart",
                                    className="chart-container",
                                    config={'displayModeBar': False},
                                    style={'height': '350px'}
                                )
                            ]
                        )
                    ], className="chart-body-fixed")
                ], className="chart-card"),
                width=12
            )
        ]),
        
        # Additional Chart - Top CNQ by Category
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Top 10 Chaînes par CNQ", className="mb-0 text-center"),
                        dbc.ButtonGroup([
                            dbc.Button("Chaîne", id="top-chain-btn", color="primary", outline=False, size="sm", n_clicks=1, className="mx-1"),
                            dbc.Button("Opération", id="top-operation-btn", color="primary", outline=True, size="sm", n_clicks=0, className="mx-1"),
                            dbc.Button("Contrôleur", id="top-controller-btn", color="primary", outline=True, size="sm", n_clicks=0, className="mx-1")
                        ], className="float-end")
                    ], className="d-flex justify-content-between align-items-center"),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-top",
                            type="circle",
                            children=[
                                dcc.Graph(
                                    id="top-chart",
                                    className="chart-container",
                                    config={'displayModeBar': False},
                                    style={'height': '350px'}
                                )
                            ]
                        )
                    ], className="chart-body-fixed")
                ], className="chart-card"),
                width=12
            )
        ])
    ], className="dashboard-container")
