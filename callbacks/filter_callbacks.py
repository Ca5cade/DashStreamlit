from dash import Output, Input, State, callback_context
import dash_bootstrap_components as dbc
from utils.filter_utils import apply_date_filter, apply_categorical_filter

def register_filter_callbacks(app, data):
    @app.callback(
        Output("additional-filters", "is_open"),
        [Input("toggle-filters-button", "n_clicks")],
        [State("additional-filters", "is_open")]
    )
    def toggle_additional_filters(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open
        
    @app.callback(
        [Output("filter-period", "start_date"),
         Output("filter-period", "end_date"),
         Output("filter-chain", "value"),
         Output("filter-operation", "value"),
         Output("filter-controller", "value"),
         Output("filter-cnq-min", "value"),
         Output("filter-cnq-max", "value"),
         Output("filter-cnq-pct-min", "value"),
         Output("filter-cnq-pct-max", "value"),
         Output("toggle-filters-button", "children")],
        [Input("reset-filters-button", "n_clicks"),
         Input("additional-filters", "is_open")]
    )
    def reset_filters(n_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            # No trigger (initial load)
            button_text = "Afficher plus de filtres"
            return None, None, None, None, None, None, None, None, None, button_text
            
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == "reset-filters-button" and n_clicks:
            # Reset all filters
            return None, None, None, None, None, None, None, None, None, "Afficher plus de filtres"
        
        if trigger_id == "additional-filters":
            # Update toggle button text based on whether filters are shown
            if is_open:
                button_text = "Masquer les filtres"
            else:
                button_text = "Afficher plus de filtres"
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, button_text
            
        # If no condition met, don't update anything
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
    @app.callback(
        Output('filter-loading-output', 'children'),
        [Input('filter-period', 'start_date'),
         Input('filter-period', 'end_date'),
         Input('filter-chain', 'value'),
         Input('filter-operation', 'value'),
         Input('filter-controller', 'value'),
         Input('filter-cnq-min', 'value'),
         Input('filter-cnq-max', 'value'),
         Input('filter-cnq-pct-min', 'value'),
         Input('filter-cnq-pct-max', 'value')]
    )
    def update_filter_status(start_date, end_date, chains, operations, controllers, cnq_min, cnq_max, cnq_pct_min, cnq_pct_max):
        # Gets called whenever filters change
        active_filters = []
        
        if start_date and end_date:
            active_filters.append(f"Période: du {start_date} au {end_date}")
        elif start_date:
            active_filters.append(f"Période: depuis {start_date}")
        elif end_date:
            active_filters.append(f"Période: jusqu'au {end_date}")
            
        if chains and len(chains) > 0:
            if len(chains) <= 3:
                active_filters.append(f"Chaîne: {', '.join(chains)}")
            else:
                active_filters.append(f"Chaîne: {len(chains)} sélectionnés")
                
        if operations and len(operations) > 0:
            if len(operations) <= 3:
                active_filters.append(f"Opération: {', '.join(operations)}")
            else:
                active_filters.append(f"Opération: {len(operations)} sélectionnés")
                
        if controllers and len(controllers) > 0:
            if len(controllers) <= 3:
                active_filters.append(f"Contrôleur: {', '.join(controllers)}")
            else:
                active_filters.append(f"Contrôleur: {len(controllers)} sélectionnés")
                
        if cnq_min is not None or cnq_max is not None:
            if cnq_min is not None and cnq_max is not None:
                active_filters.append(f"CNQ: de {cnq_min} à {cnq_max}")
            elif cnq_min is not None:
                active_filters.append(f"CNQ: min {cnq_min}")
            else:
                active_filters.append(f"CNQ: max {cnq_max}")
                
        if cnq_pct_min is not None or cnq_pct_max is not None:
            if cnq_pct_min is not None and cnq_pct_max is not None:
                active_filters.append(f"%CNQ: de {cnq_pct_min}% à {cnq_pct_max}%")
            elif cnq_pct_min is not None:
                active_filters.append(f"%CNQ: min {cnq_pct_min}%")
            else:
                active_filters.append(f"%CNQ: max {cnq_pct_max}%")
                
        if active_filters:
            return dbc.Alert(
                children=[
                    html.H6("Filtres actifs:", className="alert-heading mb-2"),
                    html.Ul([html.Li(flt) for flt in active_filters], className="mb-0")
                ],
                color="info",
                className="py-2 mt-2 mb-0"
            )
        else:
            return dbc.Alert("Aucun filtre actif", color="secondary", className="py-2 mt-2 mb-0")
            
    return
