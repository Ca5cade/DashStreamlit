from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_ag_grid import AgGrid

def create_analytics_layout(data):
    # Define important columns to show in filters
    important_columns = [
        'Chaîne', 'Opération', 'Contrôleur (se)', 'DATE', 'Qtte OF',
        'CNQ', 'CNQ_Percentage', 'Retouche', 'Rebut', 'Penalite'
    ]
    
    # Get available columns from data
    available_columns = [col for col in important_columns if col in data.columns]
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Data Extraction", className="mb-0"),
                        html.P("Extract and analyze data using filters", className="text-muted small mb-0")
                    ]),
                    dbc.CardBody([
                        # Date Range Filter
                        dbc.Row([
                            dbc.Col([
                                html.Label("Date Range", className="mb-2"),
                                dcc.DatePickerRange(
                                    id='analytics-date-range',
                                    start_date=data['DATE'].min() if 'DATE' in data.columns else None,
                                    end_date=data['DATE'].max() if 'DATE' in data.columns else None,
                                    className="mb-3"
                                )
                            ])
                        ]),
                        
                        # Main Filters
                        dbc.Row([
                            dbc.Col([
                                html.Label("Chain", className="mb-2"),
                                dcc.Dropdown(
                                    id='analytics-chain',
                                    options=[{'label': x, 'value': x} for x in data['Chaîne'].unique()] if 'Chaîne' in data.columns else [],
                                    multi=True,
                                    placeholder="Select Chain",
                                    className="mb-3"
                                )
                            ], width=4),
                            dbc.Col([
                                html.Label("Operation", className="mb-2"),
                                dcc.Dropdown(
                                    id='analytics-operation',
                                    options=[{'label': x, 'value': x} for x in data['Opération'].unique()] if 'Opération' in data.columns else [],
                                    multi=True,
                                    placeholder="Select Operation",
                                    className="mb-3"
                                )
                            ], width=4),
                            dbc.Col([
                                html.Label("Controller", className="mb-2"),
                                dcc.Dropdown(
                                    id='analytics-controller',
                                    options=[{'label': x, 'value': x} for x in data['Contrôleur (se)'].unique()] if 'Contrôleur (se)' in data.columns else [],
                                    multi=True,
                                    placeholder="Select Controller",
                                    className="mb-3"
                                )
                            ], width=4)
                        ]),
                        
                        # Metrics Selection
                        dbc.Row([
                            dbc.Col([
                                html.Label("Metrics", className="mb-2"),
                                dcc.Dropdown(
                                    id='analytics-metrics',
                                    options=[
                                        {'label': col, 'value': col}
                                        for col in ['CNQ', 'CNQ_Percentage', 'Retouche', 'Rebut', 'Penalite']
                                        if col in data.columns
                                    ],
                                    multi=True,
                                    placeholder="Select Metrics",
                                    className="mb-3"
                                )
                            ])
                        ]),
                        
                        # Group By Selection
                        dbc.Row([
                            dbc.Col([
                                html.Label("Group By", className="mb-2"),
                                dcc.Dropdown(
                                    id='analytics-groupby',
                                    options=[
                                        {'label': 'Chain', 'value': 'Chaîne'},
                                        {'label': 'Operation', 'value': 'Opération'},
                                        {'label': 'Controller', 'value': 'Contrôleur (se)'},
                                        {'label': 'Day', 'value': 'DATE'},
                                        {'label': 'Month', 'value': 'Month'},
                                        {'label': 'Year', 'value': 'Year'}
                                    ],
                                    multi=True,
                                    placeholder="Select Grouping",
                                    className="mb-3"
                                )
                            ])
                        ]),
                        
                        # Action Buttons
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "Apply Filters",
                                    id="analytics-apply",
                                    color="primary",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    "Export Data",
                                    id="analytics-export",
                                    color="success",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    "Reset Filters",
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
                        html.H5("Results", className="mb-0"),
                        html.Div(id="results-summary", className="text-muted small")
                    ]),
                    dbc.CardBody([
                        # Loading spinner
                        dbc.Spinner(
                            children=[
                                # Data table
                                html.Div(id='analytics-table', className="mb-4"),
                                
                                # Summary statistics
                                html.Div(id='analytics-summary', className="mb-4"),
                                
                                # Visualization
                                dcc.Graph(id='analytics-chart')
                            ],
                            color="primary",
                            type="border",
                            fullscreen=False
                        )
                    ])
                ])
            ])
        ])
    ])