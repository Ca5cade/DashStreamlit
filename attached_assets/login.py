from dash import html, dcc
import dash_bootstrap_components as dbc

def create_login_layout():
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    # Company branding section
                    html.Div([
                        html.Img(src="/assets/kw.png", className="login-logo mb-3"),
                        html.H1("KnitWear Manufacturing", className="text-center company-title mb-4")
                    ], className="text-center mb-5"),
                    
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-user-shield fa-3x mb-4", style={"color": "#2dcecc"}),
                                html.H2("Welcome Back", className="text-center mb-4"),
                                html.P("Please sign in to continue", className="text-muted text-center mb-4"),
                                
                                dbc.Input(
                                    id="username-input",
                                    type="text",
                                    placeholder="Username",
                                    className="mb-3 login-input"
                                ),
                                
                                dbc.Input(
                                    id="password-input",
                                    type="password",
                                    placeholder="Password",
                                    className="mb-4 login-input"
                                ),
                                
                                html.Div(id="login-error", className="text-danger mb-3"),
                                
                                dbc.Button(
                                    "Sign In",
                                    id="login-button",
                                    color="primary",
                                    className="w-100 mb-3 login-button",
                                    n_clicks=0
                                ),
                                
                                html.P([
                                    "Demo credentials: ",
                                    html.Span("admin / admin", className="text-muted")
                                ], className="text-center mb-0 small")
                            ], className="login-form")
                        ])
                    ], className="login-card")
                ], width={"size": 6, "offset": 3}, lg={"size": 4, "offset": 4})
            ], className="min-vh-100 align-items-center")
        ], fluid=True)
    ], className="login-container")