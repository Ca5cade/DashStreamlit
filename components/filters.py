import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
import traceback
from datetime import datetime, timedelta

def create_filters(data):
    try:
        # Initialize filter options
        chain_options = []
        operation_options = []
        controller_options = []
        
        # Get unique values for each filter
        if 'Chaine' in data.columns:
            chain_options = [{"label": str(val), "value": str(val)} 
                           for val in sorted(data['Chaine'].dropna().unique())]
        
        if 'Operation' in data.columns:
            operation_options = [{"label": str(val), "value": str(val)} 
                               for val in sorted(data['Operation'].dropna().unique())]
        
        if 'Controleur' in data.columns:
            controller_options = [{"label": str(val), "value": str(val)} 
                                for val in sorted(data['Controleur'].dropna().unique())]
        
        # Get date range
        start_date = data['DATE'].min() if 'DATE' in data.columns else datetime.now() - timedelta(days=30)
        end_date = data['DATE'].max() if 'DATE' in data.columns else datetime.now()
        
        return dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H5("Filtres", className="card-title mb-0"),
                    html.Div(id="filter-status", className="filter-status mt-1")
                ])
            ], className="d-flex justify-content-between align-items-center"),
            dbc.CardBody([
                # Loading spinner for filter updates
                dbc.Spinner(
                    id="filter-loading",
                    color="primary",
                    type="grow",
                    fullscreen=False,
                    children=[html.Div(id="filter-loading-output")],
                    spinner_class_name="filter-spinner"
                ),
                
                dbc.Row([
                    # Period filter (date range) - Default filter
                    dbc.Col([
                        html.Label("Période", className="filter-label"),
                        dcc.DatePickerRange(
                            id="filter-period",
                            start_date=start_date.date() if isinstance(start_date, pd.Timestamp) else start_date,
                            end_date=end_date.date() if isinstance(end_date, pd.Timestamp) else end_date,
                            display_format='DD/MM/YYYY',
                            className="w-100 mb-3",
                            clearable=True,
                            updatemode='bothdates'
                        )
                    ], width=6),
                    
                    # Chain filter (dropdown) - Default filter
                    dbc.Col([
                        html.Label("Chaîne", className="filter-label"),
                        dcc.Dropdown(
                            id="filter-chain",
                            options=chain_options,
                            multi=True,
                            placeholder="Sélectionner Chaîne",
                            className="filter-dropdown mb-3",
                            clearable=True
                        )
                    ], width=6)
                ]),
                
                # Collapsible section for additional filters
                dbc.Collapse([
                    html.Hr(className="my-2"),
                    html.H6("Filtres additionnels", className="mb-3"),
                    
                    dbc.Row([
                        # Operation filter
                        dbc.Col([
                            html.Label("Opération", className="filter-label"),
                            dcc.Dropdown(
                                id="filter-operation",
                                options=operation_options,
                                multi=True,
                                placeholder="Sélectionner Opération",
                                className="filter-dropdown mb-3",
                                clearable=True
                            )
                        ], width=6),
                        
                        # Controller filter
                        dbc.Col([
                            html.Label("Contrôleur", className="filter-label"),
                            dcc.Dropdown(
                                id="filter-controller",
                                options=controller_options,
                                multi=True,
                                placeholder="Sélectionner Contrôleur",
                                className="filter-dropdown mb-3",
                                clearable=True
                            )
                        ], width=6)
                    ]),
                    
                    # Metric filters
                    dbc.Row([
                        dbc.Col([
                            html.Label("Filtres des métriques", className="filter-label"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("CNQ Min", className="filter-label small"),
                                    dbc.Input(
                                        id="filter-cnq-min",
                                        type="number",
                                        placeholder="Min",
                                        className="form-control form-control-sm"
                                    )
                                ], width=3),
                                dbc.Col([
                                    html.Label("CNQ Max", className="filter-label small"),
                                    dbc.Input(
                                        id="filter-cnq-max",
                                        type="number",
                                        placeholder="Max",
                                        className="form-control form-control-sm"
                                    )
                                ], width=3),
                                dbc.Col([
                                    html.Label("%CNQ Min", className="filter-label small"),
                                    dbc.Input(
                                        id="filter-cnq-pct-min",
                                        type="number",
                                        placeholder="Min %",
                                        className="form-control form-control-sm"
                                    )
                                ], width=3),
                                dbc.Col([
                                    html.Label("%CNQ Max", className="filter-label small"),
                                    dbc.Input(
                                        id="filter-cnq-pct-max",
                                        type="number",
                                        placeholder="Max %",
                                        className="form-control form-control-sm"
                                    )
                                ], width=3)
                            ])
                        ], width=12)
                    ], className="mb-2")
                ], id="additional-filters", is_open=False),
                
                # Filter action buttons
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Afficher plus de filtres",
                            id="toggle-filters-button",
                            color="link",
                            size="sm",
                            className="mt-2 me-2"
                        ),
                        dbc.Button(
                            "Réinitialiser les filtres",
                            id="reset-filters-button",
                            color="link",
                            size="sm",
                            className="mt-2 text-danger"
                        )
                    ], width=12, className="text-center")
                ])
            ])
        ], className="filter-card mb-4")

    except Exception as e:
        print(f"Error creating filters: {str(e)}")
        print(traceback.format_exc())
        return html.Div("Error loading filters. Please check the console for details.")
