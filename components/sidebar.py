from dash import html
import dash_bootstrap_components as dbc

def create_sidebar():
    return html.Div([
        html.Div([
            html.H2("Strategic Dashboard", className="sidebar-title"),
            html.Hr(className="sidebar-divider"),
        ], className="sidebar-header"),
        
        dbc.Nav([
            dbc.NavLink([
                html.I(className="fas fa-home me-2"),
                "Home"
            ], href="/", active="exact", className="nav-link"),
            
            dbc.NavLink([
                html.I(className="fas fa-chart-line me-2"),
                "Analytics"
            ], href="/analytics", active="exact", className="nav-link"),
            
            dbc.NavLink([
                html.I(className="fas fa-file-alt me-2"),
                "Reports"
            ], href="/reports", active="exact", className="nav-link"),
            
            dbc.NavLink([
                html.I(className="fas fa-cog me-2"),
                "Settings"
            ], href="/settings", active="exact", className="nav-link"),

            # Dashboards Dropdown
            dbc.DropdownMenu(
                label=[
                    html.I(className="fas fa-tachometer-alt me-2"),
                    "Dashboards"
                ],
                children=[
                    dbc.DropdownMenuItem("Operational Dashboard", href="/operational"),
                    dbc.DropdownMenuItem("Tactical Dashboard", href="/tactical"),
                ],
                nav=True,
                in_navbar=True,
                color="link",
                className="nav-link",
                id="dashy",
                toggle_style={"color": "rgba(255, 255, 255, 0.6)"}
            ),
            dbc.NavLink([
                html.I(className="fas fa-sign-out-alt me-2"),
                "Logout"
            ], href="/login", id="logout-button", className="nav-link mt-auto"),
        ], vertical=True, pills=True, className="sidebar-nav"),

        html.Div([
            html.P("KnitWear Manufacturing", className="company-name")
        ], className="sidebar-footer")
    ], className="sidebar")
