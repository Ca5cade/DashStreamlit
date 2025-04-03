import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Set page configuration
st.set_page_config(
    page_title="KnitWear Manufacturing Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
try:
    with open('attached_assets/data_filter.css', 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except:
    st.markdown("""
    <style>
    .metric-card {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 15px;
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    .metric-icon {
        font-size: 24px;
        margin-right: 10px;
        color: #2dcecc;
    }
    .metric-content {
        flex-grow: 1;
    }
    .metric-title {
        font-size: 16px;
        font-weight: bold;
    }
    .metric-desc {
        font-size: 12px;
        color: #a6a6a6;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        margin-top: 5px;
        color: white;
    }
    .warning-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .warning-message button {
        background: none;
        border: none;
        color: #c62828;
        cursor: pointer;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Session state initialization for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"
if 'dashboard_type' not in st.session_state:
    st.session_state.dashboard_type = "strategic"
if 'user_role' not in st.session_state:
    st.session_state.user_role = "standard"
# Add session state for warning message
if 'show_warning' not in st.session_state:
    st.session_state.show_warning = True

# Add a session state variable for rework factor if it doesn't exist
if 'rework_factor' not in st.session_state:
    st.session_state.rework_factor = 3

# Data loading function
@st.cache_data(ttl=600)
def load_data(version=1):  # Add version parameter to force cache reset
    """Load and preprocess the dataset from res.csv"""
    # Force clear the cache
    load_data.clear()
    print("Cache cleared! Loading data with new CNQ calculation...")
    try:
        # First try the attached_assets path
        csv_path = "attached_assets/res.csv"
        if not os.path.exists(csv_path):
            # Fallback to root directory
            csv_path = "res.csv"
        
        if os.path.exists(csv_path):
            try:
                print("Loading CSV file with new CNQ calculation (v2)...")
                # Load with proper encoding detection
                try:
                    data = pd.read_csv(csv_path, encoding='utf-8')
                except UnicodeDecodeError:
                    data = pd.read_csv(csv_path, encoding='latin1')
                    
                # Ensure data types are correct
                # Convert date columns to datetime
                if 'DATE' in data.columns:
                    data['DATE'] = pd.to_datetime(data['DATE'], errors='coerce')
                elif 'date' in data.columns:
                    data['DATE'] = pd.to_datetime(data['date'], errors='coerce')
                
                # Extract month and year for easy filtering
                if 'DATE' in data.columns:
                    data['Month'] = data['DATE'].dt.month
                    data['Year'] = data['DATE'].dt.year
                    
                # Standardize column names for consistency based on the actual CSV columns
                column_mapping = {
                    'IDChaineMontage': 'Chaine',
                    'IDchainemontage': 'Chaine',  # Case sensitive match
                    'IDChaineMontage1': 'Chaine',
                    'IDChaineMontage2': 'Chaine',
                    'IDOperation': 'Operation',
                    'IDoperation': 'Operation',  # Case sensitive match
                    'IDOperation1': 'Operation',
                    'Operation': 'OperationName',
                    'IDControleur': 'Controleur',
                    'IDcontroleur': 'Controleur',  # Case sensitive match as mentioned by user
                    'Qtte': 'Quantite',
                    'Quantite': 'Quantite',
                    'Quantite2': 'Quantite2',
                    'QtteLct': 'QtteLct',
                    'QtteLct2': 'QtteLct2',
                    'QtteSondee': 'QtteSondee',
                    'NbrReclamations': 'NbrReclamations',
                    'DATE': 'DATE',
                    'DeuxiemeChoix': 'DeuxiemeChoix',
                    'Note': 'Note',
                    'ValeurOF': 'ValeurOF',
                    'Libelle': 'Libelle'
                }
                
                # Apply column mapping where columns exist
                for old_col, new_col in column_mapping.items():
                    if old_col in data.columns:
                        data[new_col] = data[old_col]
                
                # Calculate CNQ components based on the NEW formula
                # CNQ = (Qté with defect × Rework cost per unit) + (Cut quantity × Scrap cost per unit) + (Sum of penalties per defect)
                
                # Get rework factor from session state
                rework_factor = st.session_state.rework_factor
                
                # 1. Rework cost calculation
                # Check for temps (unit time) and tauxhoraire (hourly rate) columns
                if 'temps' in data.columns and 'tauxhoraire' in data.columns:
                    # Calculate unit rework cost
                    data['CoutRetoucheUnitaire'] = data['temps'] * data['tauxhoraire'] * rework_factor
                    
                    # Calculate total rework cost if we have defect quantity
                    if 'NbrReclamations' in data.columns:
                        data['Retouche'] = data['NbrReclamations'].fillna(0) * data['CoutRetoucheUnitaire']
                    else:
                        data['Retouche'] = 0
                else:
                    # Fallback to old calculation
                    if 'NbrReclamations' in data.columns:
                        rework_cost = 50  # Default cost per rework
                        data['CoutRetoucheUnitaire'] = rework_cost
                        data['Retouche'] = data['NbrReclamations'].fillna(0) * rework_cost
                    else:
                        data['CoutRetoucheUnitaire'] = 0
                        data['Retouche'] = 0
                
                # 2. Scrap cost calculation
                # Check for prix (price) column
                if 'prix' in data.columns:
                    # Use price as scrap cost per unit
                    data['CoutRebutUnitaire'] = data['prix']
                    
                    # Calculate total scrap cost if we have second choice quantity
                    if 'DeuxiemeChoix' in data.columns:
                        data['Rebut'] = data['DeuxiemeChoix'].fillna(0) * data['CoutRebutUnitaire']
                    else:
                        data['Rebut'] = 0
                else:
                    # Fallback to old calculation
                    if 'DeuxiemeChoix' in data.columns:
                        scrap_cost = 100  # Default cost per scrapped item
                        data['CoutRebutUnitaire'] = scrap_cost
                        data['Rebut'] = data['DeuxiemeChoix'].fillna(0) * scrap_cost
                    else:
                        data['CoutRebutUnitaire'] = 0
                        data['Rebut'] = 0
                
                # 3. Penalty calculation
                # Check for new penalty columns
                if 'MontantPenalite' in data.columns:
                    # Use direct penalty amount
                    data['Penalite'] = data['MontantPenalite'].fillna(0)
                else:
                    # Fallback to old calculation
                    if 'Note' in data.columns:
                        penalty_cost = 75  # Default cost per penalty point
                        data['Penalite'] = data['Note'].fillna(0) * penalty_cost
                    else:
                        data['Penalite'] = 0
                
                # Calculate total CNQ
                data['CNQ'] = data['Retouche'] + data['Rebut'] + data['Penalite']
                
                # Calculate CNQ percentage - with reasonable limits
                if 'ValeurOF' in data.columns and data['ValeurOF'].sum() > 0:
                    # Use ValeurOF as the base for percentage calculation
                    data['CNQ_Percentage'] = (data['CNQ'] / data['ValeurOF'].replace(0, np.nan)) * 100
                elif 'Quantite' in data.columns:
                    # Fallback to using quantity with assumed unit price
                    unit_price = 100  # Assumed price per unit
                    data['Quantite'] = data['Quantite'].fillna(0)
                    total_value = data['Quantite'] * unit_price
                    data['CNQ_Percentage'] = (data['CNQ'] / total_value.replace(0, np.nan)) * 100
                else:
                    data['CNQ_Percentage'] = 0

                # Cap the CNQ percentage at a reasonable maximum (e.g., 100%)
                data['CNQ_Percentage'] = data['CNQ_Percentage'].clip(upper=100)
                
                # Fill NaN values with 0
                data = data.fillna(0)
                
                # Get operation name if available
                if 'Operation' in data.columns and 'Libelle' in data.columns:
                    data['OperationName'] = data['Libelle']
                elif 'Operation' in data.columns and 'libelle' in data.columns:
                    data['OperationName'] = data['libelle']
                elif 'operation' in data.columns:
                    data['Operation'] = data['operation']
                    data['OperationName'] = data['operation']
                
                return data
                
            except Exception as e:
                st.error(f"Error loading CSV: {str(e)}")
                return create_sample_data()
        else:
            st.warning("CSV file not found, creating sample data")
            return create_sample_data()
            
    except Exception as e:
        st.error(f"Unexpected error in load_data: {str(e)}")
        return create_sample_data()

# Update the create_sample_data function to use the rework factor from session state
def create_sample_data():
    """Create sample data for testing when CSV cannot be loaded"""
    st.warning("Using sample data with NEW CNQ calculation formula")
    
    # Create date range
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    n_rows = len(dates)
    
    # Create sample data
    data = pd.DataFrame({
        'DATE': dates,
        'Chaine': np.random.choice(['CH1', 'CH2', 'CH3'], n_rows),
        'Operation': np.random.choice(['OP1', 'OP2', 'OP3', 'OP4'], n_rows),
        'Controleur': np.random.choice(['CTR1', 'CTR2', 'CTR3'], n_rows),
        'Quantite': np.random.randint(100, 1000, n_rows),
        'NbrReclamations': np.random.poisson(2, n_rows),
        'DeuxiemeChoix': np.random.binomial(1, 0.05, n_rows),
        'temps': np.random.uniform(0.5, 2.0, n_rows),  # Unit time in hours
        'tauxhoraire': np.random.choice([15, 20, 25], n_rows),  # Hourly rate
        'prix': np.random.uniform(50, 200, n_rows),  # Unit price
        'MontantPenalite': np.random.uniform(0, 100, n_rows),  # Penalty amount
        'TypeDefaut': np.random.choice(['Type A', 'Type B', 'Type C'], n_rows)  # Defect type
    })
    
    # Extract month and year
    data['Month'] = data['DATE'].dt.month
    data['Year'] = data['DATE'].dt.year
    
    # Calculate CNQ components using NEW formula
    rework_factor = st.session_state.rework_factor
    
    # 1. Rework cost calculation
    data['CoutRetoucheUnitaire'] = data['temps'] * data['tauxhoraire'] * rework_factor
    data['Retouche'] = data['NbrReclamations'] * data['CoutRetoucheUnitaire']
    
    # 2. Scrap cost calculation
    data['CoutRebutUnitaire'] = data['prix']
    data['Rebut'] = data['DeuxiemeChoix'] * data['CoutRebutUnitaire']
    
    # 3. Penalty calculation
    data['Penalite'] = data['MontantPenalite']
    
    # Calculate total CNQ
    data['CNQ'] = data['Retouche'] + data['Rebut'] + data['Penalite']
    
    # Calculate CNQ percentage with reasonable limits
    unit_price = 100  # Assumed price per unit
    total_value = data['Quantite'] * unit_price
    data['CNQ_Percentage'] = (data['CNQ'] / total_value.replace(0, np.nan)) * 100
    data['CNQ_Percentage'] = data['CNQ_Percentage'].clip(upper=100)  # Cap at 100%
    
    return data

# Import utility functions
from utils import apply_date_filter, apply_categorical_filter, apply_numerical_filter
from utils import apply_all_filters, calculate_aggregations, create_graph, create_gauge_chart

# Function to dismiss warning
def dismiss_warning():
    st.session_state.show_warning = False

# Login page
def login_page():
    # Display the logo at the top of the login page
    _, col_logo, _ = st.columns([1, 0.5, 1])
    with col_logo:
        st.image("logo.png", width=450)
        
    st.markdown("""
    <div class="login-container">
        <div class="login-form">
            <h1 class="company-title mb-4">KnitWear Manufacturing</h1>
            <h2>Welcome Back</h2>
            <p class="text-muted mb-4">Please sign in to continue</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", placeholder="Enter your password", type="password")
        login_button = st.button("Sign In", use_container_width=True)
        
        st.markdown("""
        <p style="text-align: center; margin-top: 10px;">
            <span>Demo credentials: </span>
            <span style="color: gray;">admin / admin</span>, 
            <span style="color: gray;">tact / tact</span>, or 
            <span style="color: gray;">oper / oper</span>
        </p>
        """, unsafe_allow_html=True)
        
        if login_button:
            if username == "admin" and password == "admin":
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.current_page = "dashboard"
                st.session_state.dashboard_type = "strategic"
                st.session_state.user_role = "admin"
                st.session_state.show_warning = True  # Reset warning on login
                st.rerun()
            elif username == "tact" and password == "tact":
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.current_page = "dashboard"
                st.session_state.dashboard_type = "tactical"
                st.session_state.user_role = "tactical"
                st.session_state.show_warning = True  # Reset warning on login
                st.rerun()
            elif username == "oper" and password == "oper":
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.current_page = "dashboard"
                st.session_state.dashboard_type = "operational"
                st.session_state.user_role = "operational"
                st.session_state.show_warning = True  # Reset warning on login
                st.rerun()
            else:
                st.error("Invalid username or password")

# Create sidebar
def create_sidebar():
    with st.sidebar:
        # Add logo to the sidebar
        st.image("logo.png", width=100)
        
        # Show different dashboard title based on user type
        if st.session_state.dashboard_type == "tactical":
            st.markdown("## Tactical Dashboard")
        elif st.session_state.dashboard_type == "operational":
            st.markdown("## Operational Dashboard")
        else:
            st.markdown("## Strategic Dashboard")
        st.markdown("---")
        
        # Navigation links
        selected = st.radio(
            "Navigation",
            ["Home", "Analytics", "Reports"],
            format_func=lambda x: f"{x}"
        )
        
        if selected == "Home" and st.session_state.current_page != "dashboard":
            st.session_state.current_page = "dashboard"
            st.rerun()
        elif selected == "Analytics" and st.session_state.current_page != "analytics":
            st.session_state.current_page = "analytics"
            st.rerun()
        elif selected == "Reports" and st.session_state.current_page != "reports":
            st.session_state.current_page = "reports"
            st.rerun()
        
        st.markdown("---")
        
        # User info and logout
        st.markdown(f"Logged in as: **{st.session_state.username}**")
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.current_page = "login"
            st.rerun()
        
        st.markdown("---")
        st.markdown("### KnitWear Manufacturing")

# Create header
def create_header():
    col1, col2 = st.columns([1, 5])
    with col1:
        # Display the company logo instead of the icon
        st.image("logo.png", width=450)
    with col2:
        st.title("KnitWear Manufacturing")
        if st.session_state.dashboard_type == "tactical":
            st.markdown("Dashboard Tactique (Niveau chefs services)")
        elif st.session_state.dashboard_type == "operational":
            st.markdown("Dashboard Opérationnel (Niveau Floorshop/chaînes de production)")
        else:
            st.markdown("Dashboard Stratégique (Niveau direction générale)")
    
    # Display warning message if show_warning is True
    if st.session_state.show_warning:
        warning_col1, warning_col2 = st.columns([10, 1])
        with warning_col1:
            st.markdown("""
            <div class="warning-message" text-color="red">
                <span>⚠️ Warning: any empty fields in the database will affect the dashboard output</span>
            </div>
            """, unsafe_allow_html=True)
        with warning_col2:
            if st.button("✕", key="dismiss_warning"):
                dismiss_warning()

# Create filters
def create_filters(data):
    with st.expander("Filters", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Date range filter
            st.subheader("Période")
            
            # Get min and max dates from data
            min_date = data['DATE'].min() if 'DATE' in data.columns else datetime.now() - timedelta(days=365)
            max_date = data['DATE'].max() if 'DATE' in data.columns else datetime.now()
            
            # Convert to datetime if needed
            if not isinstance(min_date, datetime):
                try:
                    min_date = pd.to_datetime(min_date)
                except:
                    min_date = datetime.now() - timedelta(days=365)
            
            if not isinstance(max_date, datetime):
                try:
                    max_date = pd.to_datetime(max_date)
                except:
                    max_date = datetime.now()
            
            start_date, end_date = st.date_input(
                "Select date range",
                value=(min_date.date(), max_date.date()),
                min_value=min_date.date(),
                max_value=max_date.date()
            )
        
        with col2:
            # Chain filter
            st.subheader("Chaîne")
            if 'idchainemontage' in data.columns:
                chain_options = sorted(data['idchainemontage'].astype(str).unique().tolist())
                selected_chains = st.multiselect("Select chains", options=chain_options)
            elif 'IDchainemontage' in data.columns:
                chain_options = sorted(data['IDchainemontage'].astype(str).unique().tolist())
                selected_chains = st.multiselect("Select chains", options=chain_options)
            elif 'Chaine' in data.columns:
                chain_options = sorted(data['Chaine'].astype(str).unique().tolist())
                selected_chains = st.multiselect("Select chains", options=chain_options)
            else:
                st.warning("No chain data available")
                selected_chains = []
        
        # Additional filters (second row)
        col3, col4 = st.columns(2)
        
        with col3:
            # Operation filter
            st.subheader("Opération")
            if 'Operation' in data.columns:
                operation_options = sorted(data['Operation'].astype(str).unique().tolist())
                selected_operations = st.multiselect("Select operations", options=operation_options)
            else:
                st.warning("No operation data available")
                selected_operations = []
        
        with col4:
            # Controller filter
            st.subheader("Contrôleur")
            if 'idcontroleur' in data.columns:
                controller_options = sorted(data['idcontroleur'].astype(str).unique().tolist())
                selected_controllers = st.multiselect("Select controllers", options=controller_options)
            elif 'IDcontroleur' in data.columns:
                controller_options = sorted(data['IDcontroleur'].astype(str).unique().tolist())
                selected_controllers = st.multiselect("Select controllers", options=controller_options)
            elif 'IDControleur' in data.columns:
                controller_options = sorted(data['IDControleur'].astype(str).unique().tolist())
                selected_controllers = st.multiselect("Select controllers", options=controller_options)
            elif 'Controleur' in data.columns:
                controller_options = sorted(data['Controleur'].astype(str).unique().tolist())
                selected_controllers = st.multiselect("Select controllers", options=controller_options)
            else:
                st.warning("No controller data available")
                selected_controllers = []
        
        # Advanced filters
        st.subheader("Metric Filters")
        adv_col1, adv_col2, adv_col3, adv_col4 = st.columns(4)
        
        with adv_col1:
            cnq_min = st.number_input("CNQ Min", min_value=0.0, step=10.0)
        with adv_col2:
            cnq_max = st.number_input("CNQ Max", min_value=0.0, step=10.0)
        with adv_col3:
            cnq_pct_min = st.number_input("%CNQ Min", min_value=0.0, max_value=100.0, step=1.0)
        with adv_col4:
            cnq_pct_max = st.number_input("%CNQ Max", min_value=0.0, max_value=100.0, step=1.0)
            
        # Add rework factor input
        st.subheader("Paramètres de calcul")
        rework_col1, rework_col2 = st.columns(2)
        with rework_col1:
            rework_factor = st.number_input("Facteur retouche", min_value=1.0, max_value=10.0, value=float(st.session_state.rework_factor), step=0.1)
            # Update session state
            if rework_factor != st.session_state.rework_factor:
                st.session_state.rework_factor = rework_factor
                # Force data reload when factor changes
                if st.button("Appliquer le nouveau facteur retouche"):
                    st.cache_data.clear()
                    st.rerun()
    
    # Return filter values
    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "chains": selected_chains,
        "operations": selected_operations,
        "controllers": selected_controllers,
        "cnq_min": cnq_min if cnq_min > 0 else None,
        "cnq_max": cnq_max if cnq_max > 0 else None,
        "cnq_pct_min": cnq_pct_min if cnq_pct_min > 0 else None,
        "cnq_pct_max": cnq_pct_max if cnq_pct_max > 0 else None,
        "rework_factor": rework_factor
    }
    
    return filters

# Dashboard metrics
def create_metrics(filtered_data):
    # Calculate metrics
    total_cnq = filtered_data['CNQ'].sum() if 'CNQ' in filtered_data.columns else 0
    
    # Calculate weighted average CNQ percentage with reasonable limits
    if 'ValeurOF' in filtered_data.columns and filtered_data['ValeurOF'].sum() > 0:
        # Use ValeurOF as the base for percentage calculation
        cnq_percentage = (filtered_data['CNQ'].sum() / filtered_data['ValeurOF'].sum()) * 100
    elif 'Quantite' in filtered_data.columns and filtered_data['Quantite'].sum() > 0:
        # Fallback to using quantity with assumed unit price
        unit_price = 100  # Assumed price per unit
        total_value = filtered_data['Quantite'].sum() * unit_price
        cnq_percentage = (filtered_data['CNQ'].sum() / total_value) * 100
    else:
        # Use the pre-calculated percentage if available
        cnq_percentage = filtered_data['CNQ_Percentage'].mean() if 'CNQ_Percentage' in filtered_data.columns else 0

    # Cap the percentage at a reasonable maximum
    cnq_percentage = min(cnq_percentage, 100)
    
    retouche = filtered_data['Retouche'].sum() if 'Retouche' in filtered_data.columns else 0
    rebut = filtered_data['Rebut'].sum() if 'Rebut' in filtered_data.columns else 0
    penalite = filtered_data['Penalite'].sum() if 'Penalite' in filtered_data.columns else 0
    
    # Get average costs per unit
    cout_retouche_unitaire = filtered_data['CoutRetoucheUnitaire'].mean() if 'CoutRetoucheUnitaire' in filtered_data.columns else 0
    cout_rebut_unitaire = filtered_data['CoutRebutUnitaire'].mean() if 'CoutRebutUnitaire' in filtered_data.columns else 0
    
    # Display calculation summary
    st.markdown("### CNQ Calculation Summary")
    st.markdown(f"""
    | Component | Formula | Total |
    |-----------|---------|-------|
    | Retouche | Qté avec défaut × Coût Retouche Unitaire | **{retouche:,.2f} TND** |
    | Rebut | Qté coupée × Coût Rebut Unitaire | **{rebut:,.2f} TND** |
    | Pénalité | Somme des pénalités | **{penalite:,.2f} TND** |
    | **CNQ Total** | Retouche + Rebut + Pénalité | **{total_cnq:,.2f} TND** |
    """)
    
    # Create metrics cards
    metrics = [
        {"title": "CNQ", "value": f"{total_cnq:,.0f} TND", "icon": "fas fa-chart-line", "desc": "Coût de la non qualité"},
        {"title": "%CNQ", "value": f"{cnq_percentage:.2f}%", "icon": "fas fa-percentage", "desc": "Taux de Coût de non qualité"},
        {"title": "Retouche", "value": f"{retouche:,.0f} TND", "icon": "fas fa-tools", "desc": f"Coût des retouches (moy: {cout_retouche_unitaire:.2f} TND/unité)"},
        {"title": "Rebut", "value": f"{rebut:,.0f} TND", "icon": "fas fa-trash-alt", "desc": f"Coût rebut (moy: {cout_rebut_unitaire:.2f} TND/unité)"}
    ]
    
    # Display metrics in columns
    cols = st.columns(4)
    
    for i, metric in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon"><i class="{metric['icon']}"></i></div>
                <div class="metric-content">
                    <div class="metric-title">{metric['title']}</div>
                    <div class="metric-desc">{metric['desc']}</div>
                    <div class="metric-value">{metric['value']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    return {
        "total_cnq": total_cnq,
        "cnq_percentage": cnq_percentage,
        "retouche": retouche,
        "rebut": rebut,
        "penalite": penalite,
        "cout_retouche_unitaire": cout_retouche_unitaire,
        "cout_rebut_unitaire": cout_rebut_unitaire
    }

# Create main dashboard charts
def create_dashboard_charts(filtered_data, metrics):
    # Create 2x2 grid for charts
    row1_col1, row1_col2 = st.columns(2)
    
    # Gauge chart
    with row1_col1:
        st.markdown("### CNQ Cumulé (en chiffre et en %)")
        
        # Set a target value for max
        if 'Quantite' in filtered_data.columns:
            total_value = filtered_data['Quantite'].sum() * 100  # Assume 100€ per unit
            max_acceptable_cnq = total_value * 0.05  # 5% of total value as maximum acceptable CNQ
        else:
            # Fallback to a reasonable multiple of current CNQ
            max_acceptable_cnq = max(10000, metrics["total_cnq"] * 2)
        
        gauge_fig = create_gauge_chart(
            value=metrics["total_cnq"],
            max_val=max_acceptable_cnq,
            title="CNQ Cumulé"
        )
        st.plotly_chart(gauge_fig, use_container_width=True)
    
    # Pie chart
    with row1_col2:
        st.markdown("### Répartition CNQ (retouche, rebut, pénalité)")
        
        # Calculate components for pie chart
        retouche = metrics["retouche"]
        rebut = metrics["rebut"]
        penalite = metrics["penalite"] if "penalite" in metrics else filtered_data['Penalite'].sum() if 'Penalite' in filtered_data.columns else 0
        
        # Create pie chart data
        labels = ['Retouche', 'Rebut', 'Pénalité']
        values = [retouche, rebut, penalite]
        
        # Check if we have non-zero values
        if sum(values) == 0:
            st.warning("Pas de données disponibles pour la répartition CNQ")
            pie_fig = go.Figure()
        else:
            pie_fig = px.pie(
                names=labels,
                values=values,
                title="Répartition CNQ",
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            
            # Update layout
            pie_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=50, b=20)
            )
        
        st.plotly_chart(pie_fig, use_container_width=True)
    
    # Line chart for trends
    st.markdown("### Courbe tendance de l'historique CNQ")
    
    # Create tabs for different time periods
    time_period_tabs = st.tabs(["Jour", "Semaine", "Mois"])
    
    # Check if we have date column
    if 'DATE' not in filtered_data.columns or filtered_data.empty:
        for tab in time_period_tabs:
            with tab:
                st.warning("Pas de données disponibles pour l'historique")
    else:
        # Day trend
        with time_period_tabs[0]:
            filtered_data_copy = filtered_data.copy()
            filtered_data_copy['TimePeriod'] = filtered_data_copy['DATE'].dt.date
            
            # Aggregate data by time period
            trend_data = filtered_data_copy.groupby('TimePeriod').agg({
                'CNQ': 'sum',
                'Retouche': 'sum',
                'Rebut': 'sum',
                'Penalite': 'sum'
            }).reset_index()
            
            # Create line chart
            line_fig = px.line(
                trend_data,
                x='TimePeriod',
                y=['CNQ', 'Retouche', 'Rebut', 'Penalite'],
                title="Évolution CNQ par jour",
                template="plotly_dark"
            )
            
            # Add moving average for CNQ
            window_size = 3 if len(trend_data) >= 3 else len(trend_data)
            if window_size > 0:
                trend_data['CNQ_MA'] = trend_data['CNQ'].rolling(window=window_size, min_periods=1).mean()
                line_fig.add_scatter(
                    x=trend_data['TimePeriod'],
                    y=trend_data['CNQ_MA'],
                    mode='lines',
                    name=f'CNQ (Moyenne mobile sur {window_size})',
                    line=dict(color='white', width=2, dash='dot')
                )
            
            # Update layout
            line_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=40, t=50, b=40),
                height=400,
                hovermode="x unified"
            )
            
            st.plotly_chart(line_fig, use_container_width=True)
        
        # Week trend
        with time_period_tabs[1]:
            filtered_data_copy = filtered_data.copy()
            # Convert date to week
            filtered_data_copy['TimePeriod'] = filtered_data_copy['DATE'].dt.isocalendar().week
            filtered_data_copy['Year_Week'] = filtered_data_copy['DATE'].dt.year.astype(str) + '-W' + filtered_data_copy['TimePeriod'].astype(str)
            
            # Aggregate data by time period
            trend_data = filtered_data_copy.groupby('Year_Week').agg({
                'CNQ': 'sum',
                'Retouche': 'sum',
                'Rebut': 'sum',
                'Penalite': 'sum'
            }).reset_index()
            
            # Create line chart
            line_fig = px.line(
                trend_data,
                x='Year_Week',
                y=['CNQ', 'Retouche', 'Rebut', 'Penalite'],
                title="Évolution CNQ par semaine",
                template="plotly_dark"
            )
            
            # Add moving average for CNQ
            window_size = 3 if len(trend_data) >= 3 else len(trend_data)
            if window_size > 0:
                trend_data['CNQ_MA'] = trend_data['CNQ'].rolling(window=window_size, min_periods=1).mean()
                line_fig.add_scatter(
                    x=trend_data['Year_Week'],
                    y=trend_data['CNQ_MA'],
                    mode='lines',
                    name=f'CNQ (Moyenne mobile sur {window_size})',
                    line=dict(color='white', width=2, dash='dot')
                )
            
            # Update layout
            line_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=40, t=50, b=40),
                height=400,
                hovermode="x unified"
            )
            
            st.plotly_chart(line_fig, use_container_width=True)
        
        # Month trend
        with time_period_tabs[2]:
            filtered_data_copy = filtered_data.copy()
            # Convert date to month
            filtered_data_copy['MonthYear'] = filtered_data_copy['DATE'].dt.strftime('%Y-%m')
            
            # Aggregate data by time period
            trend_data = filtered_data_copy.groupby('MonthYear').agg({
                'CNQ': 'sum',
                'Retouche': 'sum',
                'Rebut': 'sum',
                'Penalite': 'sum'
            }).reset_index()
            
            # Create line chart
            line_fig = px.line(
                trend_data,
                x='MonthYear',
                y=['CNQ', 'Retouche', 'Rebut', 'Penalite'],
                title="Évolution CNQ par mois",
                template="plotly_dark"
            )
            
            # Add moving average for CNQ
            window_size = 3 if len(trend_data) >= 3 else len(trend_data)
            if window_size > 0:
                trend_data['CNQ_MA'] = trend_data['CNQ'].rolling(window=window_size, min_periods=1).mean()
                line_fig.add_scatter(
                    x=trend_data['MonthYear'],
                    y=trend_data['CNQ_MA'],
                    mode='lines',
                    name=f'CNQ (Moyenne mobile sur {window_size})',
                    line=dict(color='white', width=2, dash='dot')
                )
            
            # Update layout
            line_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=40, t=50, b=40),
                height=400,
                hovermode="x unified"
            )
            
            st.plotly_chart(line_fig, use_container_width=True)
    
    # Top 10 by category
    st.markdown("### Top 10 par catégorie")
    
    # Create tabs for different categories
    category_tabs = st.tabs(["Chaîne", "Opération", "Contrôleur"])
    
    # Chain tab
    with category_tabs[0]:
        chain_col = None
        if 'idchainemontage' in filtered_data.columns and not filtered_data.empty:
            chain_col = 'idchainemontage'
        elif 'IDchainemontage' in filtered_data.columns and not filtered_data.empty:
            chain_col = 'IDchainemontage'
        elif 'Chaine' in filtered_data.columns and not filtered_data.empty:
            chain_col = 'Chaine'
            
        if chain_col:
            # Group by Chain and calculate metrics
            top_data = filtered_data.groupby(chain_col).agg({
                'CNQ': 'sum',
                'Retouche': 'sum',
                'Rebut': 'sum',
                'Penalite': 'sum'
            }).reset_index()
            
            # Sort by CNQ descending and take top 10
            top_data = top_data.sort_values('CNQ', ascending=False).head(10)
            
            # Create horizontal bar chart - SWITCHED X AND Y AXES
            bar_fig = px.bar(
                top_data,
                x=chain_col,
                y=['Retouche', 'Rebut', 'Penalite'],
                title="Top 10 Chaînes par CNQ",
                template="plotly_dark",
                orientation='v',
                barmode='stack'
            )
            
            # Update layout
            bar_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=40, t=50, b=40),
                height=400
            )
            
            st.plotly_chart(bar_fig, use_container_width=True)
        else:
            st.warning("Pas de données disponibles pour Chaîne")
    
    # Operation tab
    with category_tabs[1]:
        if 'IDOperation' in filtered_data.columns and not filtered_data.empty:
            # Group by Operation and calculate metrics
            top_data = filtered_data.groupby('IDOperation').agg({
                'CNQ': 'sum',
                'Retouche': 'sum',
                'Rebut': 'sum',
                'Penalite': 'sum'
            }).reset_index()
            
            # Sort by CNQ descending and take top 10
            top_data = top_data.sort_values('CNQ', ascending=False).head(10)
            
            # Create horizontal bar chart - SWITCHED X AND Y AXES
            bar_fig = px.bar(
                top_data,
                x='IDOperation',
                y=['Retouche', 'Rebut', 'Penalite'],
                title="Top 10 Opérations par CNQ",
                template="plotly_dark",
                orientation='v',
                barmode='stack'
            )
            
            # Update layout
            bar_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=40, t=50, b=40),
                height=400
            )
            
            st.plotly_chart(bar_fig, use_container_width=True)
        else:
            st.warning("Pas de données disponibles pour Opération")
    
    # Controller tab
    with category_tabs[2]:
        controller_col = None
        if 'idcontroleur' in filtered_data.columns and not filtered_data.empty:
            controller_col = 'idcontroleur'
        elif 'IDcontroleur' in filtered_data.columns and not filtered_data.empty:
            controller_col = 'IDcontroleur'
        elif 'IDControleur' in filtered_data.columns and not filtered_data.empty:
            controller_col = 'IDControleur'
        elif 'Controleur' in filtered_data.columns and not filtered_data.empty:
            controller_col = 'Controleur'
            
        if controller_col:
            # Group by Controller and calculate metrics
            top_data = filtered_data.groupby(controller_col).agg({
                'CNQ': 'sum',
                'Retouche': 'sum',
                'Rebut': 'sum',
                'Penalite': 'sum'
            }).reset_index()
            
            # Sort by CNQ descending and take top 10
            top_data = top_data.sort_values('CNQ', ascending=False).head(10)
            
            # Create horizontal bar chart - SWITCHED X AND Y AXES
            bar_fig = px.bar(
                top_data,
                x=controller_col,
                y=['Retouche', 'Rebut', 'Penalite'],
                title="Top 10 Contrôleurs par CNQ",
                template="plotly_dark",
                orientation='v',
                barmode='stack'
            )
            
            # Update layout
            bar_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=40, t=50, b=40),
                height=400
            )
            
            st.plotly_chart(bar_fig, use_container_width=True)
        else:
            st.warning("Pas de données disponibles pour Contrôleur")

# Create analytics page
def create_analytics_page(data):
    # Create header
    create_header()
    
    # Create filters
    filters = create_filters(data)
    
    # Apply filters
    filtered_data = apply_all_filters(data, filters)
    
    # Data extraction section
    st.markdown("## Extraction de données")
    st.markdown("Extrayez et analysez les données à l'aide de filtres")
    
    # Metrics and chart type selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Available metrics
        metrics_options = [col for col in ['CNQ', 'CNQ_Percentage', 'Retouche', 'Rebut', 'Penalite'] if col in data.columns]
        selected_metrics = st.multiselect(
            "Métriques",
            options=metrics_options,
            default=['CNQ', 'CNQ_Percentage'] if 'CNQ' in metrics_options else metrics_options[:1] if metrics_options else []
        )
    
    with col2:
        # Chart type selection
        chart_type = st.selectbox(
            "Type de graphique",
            options=['bar', 'line', 'pie', 'treemap'],
            format_func=lambda x: {'bar': 'Bar Chart', 'line': 'Line Chart', 'pie': 'Pie Chart', 'treemap': 'Treemap'}[x]
        )
    
    # Group by selection
    col3, col4 = st.columns([2, 1])
    
    with col3:
        # Group by options
        group_by_options = [
            {'label': 'Chaîne', 'value': 'idchainemontage'},
            {'label': 'Chaîne', 'value': 'IDchainemontage'},
            {'label': 'Chaîne', 'value': 'Chaine'},
            {'label': 'Opération', 'value': 'Operation'},
            {'label': 'Contrôleur', 'value': 'idcontroleur'},
            {'label': 'Contrôleur', 'value': 'IDcontroleur'},
            {'label': 'Contrôleur', 'value': 'IDControleur'},
            {'label': 'Controleur', 'value': 'Controleur'},
            {'label': 'Jour', 'value': 'DATE'},
            {'label': 'Mois', 'value': 'Month'},
            {'label': 'Année', 'value': 'Year'}
        ]
        group_by_options = [option for option in group_by_options if option['value'] in data.columns]
        
        selected_group_by = st.multiselect(
            "Regrouper par",
            options=[option['value'] for option in group_by_options],
            format_func=lambda x: next((option['label'] for option in group_by_options if option['value'] == x), x),
            default=[option['value'] for option in group_by_options if option['label'] == 'Chaîne'][:1] if any(option['label'] == 'Chaîne' for option in group_by_options) else []
        )
    
    with col4:
        # Limit results
        limit = st.selectbox(
            "Limiter résultats",
            options=[5, 10, 20, 0],
            format_func=lambda x: f"Top {x}" if x > 0 else "Tous",
            index=1
        )
    
    # Action buttons
    col5, col6, col7 = st.columns([1, 1, 3])
    
    with col5:
        apply_button = st.button("Appliquer l'analyse", use_container_width=True)
    
    with col6:
        export_button = st.button("Exporter les données", use_container_width=True)
    
    # Results section
    st.markdown("## Résultats")
    
    # Initialize result state
    if "analytics_results" not in st.session_state:
        st.session_state.analytics_results = None
    
    # Apply analytics when button is clicked
    if apply_button:
        if not filtered_data.empty and selected_metrics and selected_group_by:
            # Calculate aggregations
            aggregated_data = calculate_aggregations(filtered_data, selected_group_by, selected_metrics)
            
            # Sort by the first metric in descending order
            sort_by = selected_metrics[0] if selected_metrics else None
            if sort_by and sort_by in aggregated_data.columns:
                aggregated_data = aggregated_data.sort_values(by=sort_by, ascending=False)
            
            # Apply limit if specified
            if limit and limit > 0:
                aggregated_data = aggregated_data.head(limit)
            
            # Store results
            st.session_state.analytics_results = {
                "aggregated_data": aggregated_data,
                "chart_type": chart_type,
                "metrics": selected_metrics,
                "group_by": selected_group_by
            }
        else:
            st.error("Please select metrics and group by fields, and ensure filtered data is not empty")
    
    # Handle export
    if export_button and st.session_state.analytics_results is not None:
        # Export data as CSV
        aggregated_data = st.session_state.analytics_results["aggregated_data"]
        csv_data = aggregated_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="analytics_export.csv",
            mime="text/csv"
        )
    
    # Display results if available
    if st.session_state.analytics_results is not None:
        results = st.session_state.analytics_results
        aggregated_data = results["aggregated_data"]
        chart_type = results["chart_type"]
        metrics = results["metrics"]
        group_by = results["group_by"]
        
        # Create tabs for chart and table views
        chart_tab, table_tab = st.tabs(["Graphique", "Tableau de données"])
        
        with chart_tab:
            if chart_type == 'bar':
                if len(group_by) == 1:
                    # Simple bar chart
                    fig = px.bar(
                        aggregated_data, 
                        x=group_by[0], 
                        y=metrics,
                        title=f'{", ".join(metrics)} by {group_by[0]}',
                        barmode='group',
                        template="plotly_dark"
                    )
                else:
                    # Grouped bar chart
                    fig = px.bar(
                        aggregated_data,
                        x=group_by[0],
                        y=metrics[0] if metrics else None,
                        color=group_by[1] if len(group_by) > 1 else None,
                        title=f'{metrics[0] if metrics else ""} by {", ".join(group_by)}',
                        barmode='group',
                        template="plotly_dark"
                    )
            elif chart_type == 'line':
                if len(group_by) == 1:
                    fig = px.line(
                        aggregated_data,
                        x=group_by[0],
                        y=metrics,
                        title=f'{", ".join(metrics)} by {group_by[0]}',
                        template="plotly_dark",
                        markers=True
                    )
                else:
                    fig = px.line(
                        aggregated_data,
                        x=group_by[0],
                        y=metrics[0] if metrics else None,
                        color=group_by[1] if len(group_by) > 1 else None,
                        title=f'{metrics[0] if metrics else ""} by {", ".join(group_by)}',
                        template="plotly_dark",
                        markers=True
                    )
            elif chart_type == 'pie':
                fig = px.pie(
                    aggregated_data,
                    names=group_by[0],
                    values=metrics[0] if metrics else None,
                    title=f'{metrics[0] if metrics else ""} by {group_by[0]}',
                    template="plotly_dark"
                )
            elif chart_type == 'treemap':
                fig = px.treemap(
                    aggregated_data,
                    path=group_by,
                    values=metrics[0] if metrics else None,
                    title=f'{metrics[0] if metrics else ""} by {", ".join(group_by)}',
                    template="plotly_dark"
                )
            else:
                # Default to bar chart
                fig = px.bar(
                    aggregated_data,
                    x=group_by[0],
                    y=metrics,
                    title=f'{", ".join(metrics)} by {group_by[0]}',
                    barmode='group',
                    template="plotly_dark"
                )
            
            # Improve chart appearance
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=40, t=80, b=40),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            if not aggregated_data.empty:
                st.markdown("### Statistiques des métriques")
                
                # Create summary table
                summary_data = []
                
                for metric in metrics:
                    if metric in filtered_data.columns:
                        # Calculate statistics
                        total = filtered_data[metric].sum()
                        mean = filtered_data[metric].mean()
                        median = filtered_data[metric].median()
                        min_val = filtered_data[metric].min()
                        max_val = filtered_data[metric].max()
                        
                        # Add to summary
                        summary_data.append({
                            "Métrique": metric,
                            "Total": f"{total:,.2f}",
                            "Moyenne": f"{mean:,.2f}",
                            "Médiane": f"{median:,.2f}",
                            "Min": f"{min_val:,.2f}",
                            "Max": f"{max_val:,.2f}"
                        })
                
                # Display summary table
                st.table(pd.DataFrame(summary_data))
        
        with table_tab:
            # Show data table
            if not aggregated_data.empty:
                st.markdown(f"Affichage de {len(aggregated_data)} résultats sur {len(filtered_data)} enregistrements filtrés")
                st.dataframe(aggregated_data, use_container_width=True)
            else:
                st.warning("No data available to display")
    else:
        st.info("Utilisez les filtres et cliquez sur 'Appliquer l'analyse' pour voir les résultats")

# Create reports page
def create_reports_page(data):
    # Create header
    create_header()
    
    # Create filters
    filters = create_filters(data)
    
    # Apply filters
    filtered_data = apply_all_filters(data, filters)
    
    # Report builder layout
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("## Configuration du graphique")
        
        # Graph types
        graph_types = {
            'bar': 'Bar Chart',
            'line': 'Line Chart',
            'scatter': 'Scatter Plot',
            'pie': 'Pie Chart',
            'histogram': 'Histogram',
            'box': 'Box Plot',
            'heatmap': 'Heatmap',
            'treemap': 'Treemap'
        }
        
        graph_type = st.selectbox(
            "Type de graphique",
            options=list(graph_types.keys()),
            format_func=lambda x: graph_types[x]
        )
        
        # X-axis selection
        x_col = st.selectbox(
            "Axe X",
            options=data.columns,
            index=0 if 'Chaine' in data.columns else 0
        )
        
        # Y-axis selection
        numeric_cols = data.select_dtypes(include=['number']).columns
        y_col = st.selectbox(
            "Axe Y",
            options=numeric_cols,
            index=0 if 'CNQ' in numeric_cols else 0
        )
        
        # Color selection (optional)
        color_col = st.selectbox(
            "Grouper par couleur (Optionnel)",
            options=[None] + list(data.columns),
            index=0
        )
        
        # Add graph button
        add_graph = st.button("Ajouter graphique", use_container_width=True)
        
        # Export button
        export_pdf = st.button("Exporter PDF", use_container_width=True)
    
    with col2:
        st.markdown("## Graphiques générés")
        
        # Help text
        with st.expander("Comment utiliser les graphiques"):
            st.markdown("""
            1. Configurez votre graphique en sélectionnant le type, l'axe X, l'axe Y et éventuellement un groupement par couleur.
            2. Cliquez sur 'Ajouter graphique' pour l'ajouter au rapport.
            3. Vous pouvez ajouter plusieurs graphiques au rapport.
            4. Pour exporter en PDF, cliquez sur 'Exporter PDF' après avoir ajouté tous les graphiques souhaités.
            """)
        
        # Initialize graphs list if not exists
        if "report_graphs" not in st.session_state:
            st.session_state.report_graphs = []
        
        # Add graph when button is clicked
        if add_graph and x_col and y_col:
            # Get data for the graph
            try:
                df_for_graph = filtered_data.copy()
                
                # Convert date columns to string format for better display
                if x_col in df_for_graph.columns and pd.api.types.is_datetime64_any_dtype(df_for_graph[x_col]):
                    df_for_graph[x_col] = df_for_graph[x_col].dt.strftime('%Y-%m-%d')
                
                # For categorical columns with too many unique values, limit to top N
                if x_col in df_for_graph.columns and df_for_graph[x_col].nunique() > 20:
                    top_values = df_for_graph[x_col].value_counts().nlargest(20).index
                    df_for_graph = df_for_graph[df_for_graph[x_col].isin(top_values)]
                
                # Create the graph
                fig = create_graph(
                    graph_type=graph_type,
                    x_data=df_for_graph[x_col],
                    y_data=df_for_graph[y_col],
                    color_data=df_for_graph[color_col] if color_col else None,
                    title=f"{y_col} vs {x_col}"
                )
                
                # Add to graphs list
                graph_info = {
                    "type": graph_type,
                    "x": x_col,
                    "y": y_col,
                    "color": color_col,
                    "figure": fig
                }
                
                st.session_state.report_graphs.append(graph_info)
                
                # Success message
                st.success(f"Graph added: {graph_type} of {y_col} vs {x_col}")
            
            except Exception as e:
                st.error(f"Error creating graph: {str(e)}")
        
        # Display all graphs
        for i, graph in enumerate(st.session_state.report_graphs):
            with st.container():
                # Create a card for the graph
                st.markdown(f"### {graph['y']} vs {graph['x']} ({graph['type']})")
                
                # Display graph
                st.plotly_chart(graph['figure'], use_container_width=True)
                
                # Remove button
                if st.button(f"Remove", key=f"remove_{i}"):
                    st.session_state.report_graphs.pop(i)
                    st.rerun()
        
        # Export PDF functionality (placeholder - would need a PDF library)
        if export_pdf and st.session_state.report_graphs:
            st.info("PDF export would be implemented here. For now, you can use browser print to save as PDF.")
            # In a real implementation, would use a library like ReportLab to create PDFs

# Import tactical dashboard
from tactical_dashboard import create_tactical_dashboard

# Import operational dashboard
from operational_dashboard import create_operational_dashboard

# Dashboard page
def dashboard_page(data):
    # Check user role for dashboard type
    if st.session_state.dashboard_type == "tactical":
        # Display tactical dashboard
        create_tactical_dashboard(data)
    elif st.session_state.dashboard_type == "operational":
        # Display operational dashboard
        create_header()
        create_operational_dashboard(data)
    else:
        # Create header
        create_header()
            
        # Create filters
        filters = create_filters(data)
        
        # Apply filters
        filtered_data = apply_all_filters(data, filters)
        
        # Dashboard title and description
        st.markdown("## Dashboard Vue d'ensemble")
        st.markdown("Tableau de bord montrant les KPIs et indicateurs clés de performance qualité")
        
        # Create metrics
        metrics_values = create_metrics(filtered_data)
        
        # Create dashboard charts
        create_dashboard_charts(filtered_data, metrics_values)

# Main app
def main():
    # Clear all caches on startup
    st.cache_data.clear()
    
    # Load data with version parameter to force cache reset
    data = load_data(version=10)  # Use a higher version number
    
    # Show appropriate page based on authentication status and current page
    if not st.session_state.authenticated:
        login_page()
    else:
        # Create sidebar for navigation
        create_sidebar()
        
        # Display appropriate page based on current_page
        if st.session_state.current_page == "analytics":
            create_analytics_page(data)
        elif st.session_state.current_page == "reports":
            create_reports_page(data)
        else:  # Default to dashboard
            dashboard_page(data)

# Run the app
if __name__ == "__main__":
    main()

