import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import plotly.express as px

# Import the new dashboards
from new_operational_dashboard import create_operational_dashboard
from new_tactical_dashboard import create_tactical_dashboard

# Set page configuration
st.set_page_config(
    page_title="Tableau de Bord Qualité Production",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
with open('styles.css', 'r') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Session state initialization for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_role' not in st.session_state:
    st.session_state.user_role = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"

# Data loading function
@st.cache_data(ttl=600)
def load_data():
    """Load and preprocess the dataset from res.csv"""
    try:
        csv_path = "res.csv"
        
        if os.path.exists(csv_path):
            try:
                print("Loading CSV file...")
                # Load with proper encoding detection
                try:
                    data = pd.read_csv(csv_path, encoding='utf-8', low_memory=False)
                except UnicodeDecodeError:
                    data = pd.read_csv(csv_path, encoding='latin1', low_memory=False)
                    
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
                
                # Improve column casing for consistency
                # We'll keep the original column names but add convenience columns if needed
                data = data.copy()
                
                return data
            except Exception as e:
                print(f"Error loading CSV: {e}")
                return create_sample_data()
        else:
            print("CSV file not found, using sample data.")
            return create_sample_data()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return create_sample_data()

def create_sample_data():
    """Create sample data for testing when CSV cannot be loaded"""
    print("Creating sample data...")
    # Generate dates for the past month
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    dates = [start_date + timedelta(days=i) for i in range(31)]
    
    # Create sample data with similar structure to the expected CSV
    data = []
    chains = [1, 2, 3, 4, 5]
    categories = ["PRODUCTION FIN CHAINE", "PRODUCTION ENCOURS"]
    operations = ["Fixation manchette", "Surp elastique", "Montage col", "Fixation zip", "Surpiqure"]
    defects = ["Rebut", "Retouche"]
    controllers = [f"Controller{i}" for i in range(1, 6)]
    
    for date in dates:
        for _ in range(np.random.randint(5, 20)):  # Random number of entries per day
            data.append({
                'DATE': date,
                'IDChaineMontage': np.random.choice(chains),
                'Categorie': np.random.choice(categories),
                'Operation': np.random.choice(operations),
                'TypeDefaut': np.random.choice(defects),
                'Qtte': np.random.randint(1, 10),
                'QtteSondee': np.random.randint(10, 100),
                'QtteLct': np.random.randint(50, 200),
                'Temps': np.random.randint(5, 60),
                'TauxHoraire': np.random.uniform(10, 50),
                'IDControleur': np.random.choice(controllers),
                'IDTiers': f"Supplier{np.random.randint(1, 6)}",
                'IDOFabrication': f"OF{np.random.randint(1000, 9999)}"
            })
    
    df = pd.DataFrame(data)
    df['Month'] = df['DATE'].dt.month
    df['Year'] = df['DATE'].dt.year
    
    return df

def login_page():
    """Display the login page"""
    st.markdown(
        """
        <div class="login-container">
            <div class="login-box">
                <h1 class="login-title">Tableau de Bord</h1>
                <p class="login-subtitle">Connectez-vous pour accéder au tableau de bord</p>
        """,
        unsafe_allow_html=True
    )
    
    # Login form
    username = st.text_input("Nom d'utilisateur", key="login_username")
    password = st.text_input("Mot de passe", type="password", key="login_password")
    login_btn = st.button("Se connecter")
    
    if login_btn:
        # Simple authentication logic
        if username == "admin" and password == "admin":
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.user_role = "admin"
            st.session_state.current_page = "dashboard"
            st.rerun()
        elif username == "oper" and password == "oper":
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.user_role = "operational"
            st.session_state.current_page = "dashboard"
            st.rerun()
        elif username == "tact" and password == "tact":
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.user_role = "tactical"
            st.session_state.current_page = "dashboard"
            st.rerun()
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect.")
    
    st.markdown(
        """
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def create_sidebar():
    """Create the sidebar with navigation and filters"""
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-header">
                <div>📊 Dashboard Qualité</div>
                <div class="user-info">👤 {st.session_state.username}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Navigation options based on user role
        if st.session_state.user_role == "admin":
            selected = st.selectbox(
                "Navigation",
                ["Tableau de Bord Opérationnel", "Tableau de Bord Tactique"],
                key="admin_nav"
            )
            
            if selected == "Tableau de Bord Opérationnel":
                st.session_state.current_page = "operational"
            else:
                st.session_state.current_page = "tactical"
                
        elif st.session_state.user_role == "operational":
            st.session_state.current_page = "operational"
            
        elif st.session_state.user_role == "tactical":
            st.session_state.current_page = "tactical"
        
        # Logout button
        if st.button("Déconnexion"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.user_role = ""
            st.session_state.current_page = "login"
            st.rerun()

def show_dashboard(data):
    """Show the appropriate dashboard based on the current page"""
    if st.session_state.current_page == "operational":
        create_operational_dashboard(data)
    elif st.session_state.current_page == "tactical":
        create_tactical_dashboard(data)
    else:
        # Default to operational dashboard if page is not specified
        create_operational_dashboard(data)

def main():
    """Main function to run the application"""
    if not st.session_state.authenticated:
        login_page()
    else:
        # Create sidebar
        create_sidebar()
        
        # Load data
        data = load_data()
        
        # Show appropriate dashboard
        show_dashboard(data)

if __name__ == "__main__":
    main()