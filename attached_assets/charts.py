from dash import html, dcc
import dash_bootstrap_components as dbc

def create_charts():
    return html.Div([
        # Metrics row
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H5("CNQ", className="metric-title"),
                        html.Div([
                            html.Span("Coût de la non qualité", className="metric-description"),
                            html.Div(id="cnq-value", className="metric-value")
                        ])
                    ])
                ], className="metric-card"),
                width=6
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H5("%CNQ", className="metric-title"),
                        html.Div([
                            html.Span("Taux de Coût de non qualité", className="metric-description"),
                            html.Div(id="cnq-percentage-value", className="metric-value")
                        ])
                    ])
                ], className="metric-card"),
                width=6
            )
        ], className="mb-4"),
        
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
                    ], className="text-center"),
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
        ])
    ], className="dashboard-container")

