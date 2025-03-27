from dash import html
import dash_bootstrap_components as dbc

def create_header():
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Img(src="/assets/kw.png", className="company-logo"),
                html.Div([
                    html.H1("KnitWear Manufacturing", className="mb-0"),
                    html.P("Dashboard Stratégique (Niveau direction générale)", className="text-muted")
                ])
            ], className="d-flex align-items-center")
        ])
    ], className="header-card mb-4")

