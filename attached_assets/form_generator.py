import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd

def create_filter_fields(data):
    """
    Create filter form fields based on data columns
    
    Args:
        data: DataFrame with data
        
    Returns:
        List of form fields
    """
    form_fields = []
    
    # Define important columns to include in the form
    important_columns = [
        'IDReclamation', 'IDTypeReclamation', 'IDChaineMontage', 'IDEmploye', 
        'IDOperation', 'DATE', 'IDOFabrication', 'NumMatelas', 'NbrReclamations',
        'Chaîne', 'Opération', 'Contrôleur (se)', 'Date', 'Qtte OF',
        'Nom', 'Prenom', 'Libelle', 'Categorie'
    ]
    
    # Filter to only include columns that exist in the data
    form_columns = [col for col in important_columns if col in data.columns]
    
    # If no important columns are found, use the first 10 columns
    if not form_columns and len(data.columns) > 0:
        form_columns = data.columns[:10].tolist()
    
    for col in form_columns:
        # Determine the type of input based on the column data
        if col in data.columns:
            unique_values = data[col].dropna().unique()
            
            # For columns with few unique values, use a dropdown
            if len(unique_values) < 50:
                options = [{"label": str(val), "value": str(val)} for val in sorted(unique_values)]
                form_fields.append(
                    dbc.FormGroup([
                        html.Label(col.replace('ID', ''), className="form-label"),
                        dcc.Dropdown(
                            id={'type': 'filter', 'column': col},
                            options=options,
                            multi=True,
                            placeholder=f"Select {col.replace('ID', '')}",
                            className="form-control"
                        )
                    ], className="mb-3")
                )
            # For date columns, use a date picker
            elif pd.api.types.is_datetime64_any_dtype(data[col]) or 'date' in col.lower():
                form_fields.append(
                    dbc.FormGroup([
                        html.Label(col.replace('ID', ''), className="form-label"),
                        dcc.DatePickerRange(
                            id={'type': 'filter', 'column': col},
                            start_date_placeholder_text="Start Date",
                            end_date_placeholder_text="End Date",
                            className="form-control"
                        )
                    ], className="mb-3")
                )
            # For numeric columns, use a range slider
            elif pd.api.types.is_numeric_dtype(data[col]):
                min_val = data[col].min()
                max_val = data[col].max()
                form_fields.append(
                    dbc.FormGroup([
                        html.Label(col.replace('ID', ''), className="form-label"),
                        dcc.RangeSlider(
                            id={'type': 'filter', 'column': col},
                            min=min_val,
                            max=max_val,
                            step=(max_val - min_val) / 100,
                            marks={min_val: str(min_val), max_val: str(max_val)},
                            tooltip={"placement": "bottom", "always_visible": True},
                            className="form-control"
                        )
                    ], className="mb-3")
                )
            # For other columns, use a text input
            else:
                form_fields.append(
                    dbc.FormGroup([
                        html.Label(col.replace('ID', ''), className="form-label"),
                        dbc.Input(
                            id={'type': 'filter', 'column': col},
                            type="text",
                            placeholder=f"Enter {col.replace('ID', '')}",
                            className="form-control"
                        )
                    ], className="mb-3")
                )
    
    return html.Div(form_fields)

