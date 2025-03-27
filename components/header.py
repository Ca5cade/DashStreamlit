from dash import html
import dash_bootstrap_components as dbc

def create_header():
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className="fas fa-chart-line fa-2x me-3", style={"color": "#2dcecc"}),
                html.Div([
                    html.H1("KnitWear Manufacturing", className="mb-0"),
                    html.P("Dashboard Stratégique (Niveau direction générale)", className="text-muted")
                ])
            ], className="d-flex align-items-center")
        ])
    ], className="header-card mb-4")
