from dash import html
import dash_bootstrap_components as dbc

def create_metrics():
    metrics = [
        {"title": "CNQ", "id": "total-cnq", "icon": "fas fa-chart-line", "description": "Coût de la non qualité"},
        {"title": "%CNQ", "id": "cnq-percentage", "icon": "fas fa-percentage", "description": "Taux de Coût de non qualité"},
        {"title": "Retouche", "id": "retouche-value", "icon": "fas fa-tools", "description": "Coût des retouches"},
        {"title": "Rebut", "id": "rebut-value", "icon": "fas fa-trash-alt", "description": "Coût rebut des pièces déclassées"}
    ]
    
    return dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className=metric["icon"]),
                        html.Div([
                            html.H6(metric["title"], className="mb-0"),
                            html.P(metric["description"], className="small text-muted mb-1"),
                            html.H4(id=metric["id"], className="mb-0 metric-value")
                        ])
                    ], className="d-flex align-items-center gap-3")
                ])
            ], className="metric-card")
        , width=3) for metric in metrics
    ], className="mb-4")
