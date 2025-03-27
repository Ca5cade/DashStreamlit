from dash import Output, Input, State
import dash_bootstrap_components as dbc

def register_login_callbacks(app):
    @app.callback(
        [Output('auth-store', 'data'),
         Output('login-error', 'children'),
         Output('url', 'pathname')],
        [Input('login-button', 'n_clicks')],
        [State('username-input', 'value'),
         State('password-input', 'value')]
    )
    def login(n_clicks, username, password):
        if n_clicks is None or n_clicks == 0:
            # Initial load, don't trigger login
            return {'authenticated': False}, '', '/login'
        
        # Simple authentication check
        if username == 'admin' and password == 'admin':
            return {'authenticated': True}, '', '/'
        else:
            return {'authenticated': False}, 'Invalid username or password', '/login'
            
    @app.callback(
        [Output('auth-store', 'data', allow_duplicate=True),
         Output('url', 'pathname', allow_duplicate=True)],
        [Input('logout-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def logout(n_clicks):
        if n_clicks is None:
            return dash.no_update, dash.no_update
            
        return {'authenticated': False}, '/login'
