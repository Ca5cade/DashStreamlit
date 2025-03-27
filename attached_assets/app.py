import os
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from flask_login import LoginManager, login_user, logout_user
from config import Config
from layout.sidebar import create_sidebar
from layout.header import create_header
from layout.filters import create_filters
from layout.charts import create_charts
from layout.metrics import create_metrics
from layout.login import create_login_layout
from layout.analytics import create_analytics_layout
from callbacks import register_callbacks
from callback.analytics_callbacks import register_analytics_callbacks
from utils.data_loader import load_data
from utils.auth import User, authenticate_user, init_login_manager
from utils.app_factory import create_app
from layout.reports import create_reports_layout
from callback.reports_callbacks import register_reports_callbacks
import dash

# Initialize the app
app = create_app()
server = app.server

# Configure server
server.config.from_object(Config)

# Initialize login manager
login_manager = init_login_manager(server)

# Load data
data = load_data()

# Create the main layout with protected routes
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='login-status', storage_type='session')
])

# Callback to handle page routing
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
    [State('login-status', 'data')]
)
def display_page(pathname, login_status):
    if pathname == '/login' or not login_status:
        return create_login_layout()
    
    # Create the sidebar for all authenticated pages
    sidebar = create_sidebar()
    
    if pathname == '/analytics':
        return html.Div([
            dbc.Row([
                dbc.Col(sidebar, width=2, className="sidebar-container"),
                dbc.Col([
                    create_header(),
                    create_analytics_layout(data)
                ], width=10, className="main-content")
            ], className="g-0 dashboard-container")
        ], className="app-container")
    elif pathname == '/reports':
        return html.Div([
            dbc.Row([
                dbc.Col(sidebar, width=2, className="sidebar-container"),
                dbc.Col([
                    create_header(),
                    create_reports_layout(data)
                ], width=10, className="main-content")
            ], className="g-0 dashboard-container")
        ], className="app-container")
    
    # Default dashboard view - only using the filters from create_filters
    return html.Div([
        dbc.Row([
            dbc.Col(sidebar, width=2, className="sidebar-container"),
            dbc.Col([
                create_header(),
                create_filters(data),  # Only using this filter set
                create_metrics(),
                create_charts()
            ], width=10, className="main-content")
        ], className="g-0 dashboard-container")
    ], className="app-container")

# Login callback
@app.callback(
    [Output('login-status', 'data'),
     Output('url', 'pathname'),
     Output('login-error', 'children')],
    [Input('login-button', 'n_clicks')],
    [State('username-input', 'value'),
     State('password-input', 'value')]
)
def login_callback(n_clicks, username, password):
    if n_clicks is None:
        return None, '/login', ''
    
    if authenticate_user(username, password):
        user = User(username)
        login_user(user)
        return True, '/', ''
    
    return None, '/login', 'Invalid credentials. Please try again.'

# Logout callback
@app.callback(
    [Output('login-status', 'clear_data'),
     Output('url', 'pathname', allow_duplicate=True)],
    [Input('logout-button', 'n_clicks')],
    prevent_initial_call=True
)
def logout_callback(n_clicks):
    if n_clicks is not None:
        logout_user()
        return True, '/login'
    return False, dash.no_update

# Register all callbacks
register_callbacks(app, data)
register_analytics_callbacks(app, data)
register_reports_callbacks(app, data)

if __name__ == '__main__':
    app.run_server(debug=True)

