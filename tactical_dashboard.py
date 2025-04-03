import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import apply_date_filter

# Apply custom CSS for enhanced dark theme
def apply_dark_theme():
    st.markdown("""
    <style>
        /* Main background and text colors */
        .main {
            background-color: #0f172a;
            color: #f8fafc;
        }
        .stApp {
            background-color: #0f172a;
        }
        
        /* Input fields and widgets */
        .css-1kyxreq, .css-12oz5g7, div[data-testid="stDateInput"] > div:first-child {
            background-color: #1e293b;
            color: #f8fafc;
            border-radius: 8px;
            border: 1px solid #334155;
        }
        .st-bw, .st-c0, .st-c3, .st-c8, .st-c9, .st-ca, .st-cb, .st-cc, .st-cd, .st-ce, .st-cf, .st-cg, .st-ch {
            background-color: #1e293b;
            color: #f8fafc;
        }
        .st-bq, .st-br, .st-bs, .st-bt, .st-ae, .st-af, .st-ag {
            color: #f8fafc;
        }
        
        /* Date inputs */
        .stDateInput > div > div {
            background-color: #1e293b;
            color: #f8fafc;
        }
        .stDateInput input {
            background-color: #1e293b;
            color: #f8fafc;
        }
        
        /* Headers */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
            color: #f8fafc;
            font-weight: 600;
        }
        
        /* Custom metric containers */
        .metric-container {
            background-color: #1e293b;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #334155;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .metric-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        .metric-value {
            font-size: 26px;
            font-weight: bold;
            color: #f8fafc;
        }
        .metric-label {
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 4px;
        }
        
        /* Section headers */
        .section-header {
            background: linear-gradient(90deg, #4f46e5 0%, #6366f1 100%);
            padding: 12px;
            border-radius: 8px;
            margin: 24px 0 16px 0;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .section-title {
            color: white;
            margin: 0;
            font-size: 20px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }
        
        /* Card containers */
        .card-container {
            background-color: #1e293b;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #334155;
        }
        
        /* Dashboard header */
        .dashboard-header {
            background: linear-gradient(90deg, #4338ca 0%, #6366f1 100%);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            text-align: center;
        }
        .dashboard-title {
            color: white;
            margin: 0;
            font-size: 32px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }
        .dashboard-subtitle {
            color: rgba(255, 255, 255, 0.9);
            margin: 8px 0 0 0;
            font-size: 18px;
            font-weight: 500;
        }
        
        /* Filter section */
        .filter-container {
            background-color: #1e293b;
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
            border: 1px solid #334155;
        }
        .filter-title {
            color: #f8fafc;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 12px;
        }
        
        /* Divider */
        .divider {
            height: 1px;
            background-color: #334155;
            margin: 24px 0;
        }
        
        /* Tooltip */
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
        }
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: #334155;
            color: #f8fafc;
            text-align: center;
            border-radius: 6px;
            padding: 8px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 12px;
        }
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        
        /* Alert notice */
        .alert-notice {
            background-color: rgba(220, 38, 38, 0.1);
            border-left: 4px solid #dc2626;
            color: #fecaca;
            padding: 12px 16px;
            margin: 8px 0;
            border-radius: 4px;
            font-size: 14px;
            display: flex;
            align-items: center;
        }
        .alert-icon {
            margin-right: 12px;
            font-size: 18px;
        }
        .alert-message {
            flex-grow: 1;
        }
        .alert-column {
            font-weight: bold;
            color: #fca5a5;
        }
    </style>
    """, unsafe_allow_html=True)

# Create alert notice for missing data
def create_alert_notice(column_name):
    """
    Create an alert notice for missing data
    
    Args:
        column_name: Name of the column that needs to be filled
    """
    st.markdown(f"""
    <div class="alert-notice">
        <div class="alert-icon">⚠️</div>
        <div class="alert-message">
            Vous devez remplir cette colonne: <span class="alert-column">{column_name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Check for missing data and display alerts
def check_missing_data(filtered_data, metrics):
    """
    Check for missing data that causes metrics to be zero
    
    Args:
        filtered_data: DataFrame with production data
        metrics: Dictionary of calculated metrics
    """
    missing_columns = []
    
    # Check for retouche metrics
    if metrics['retouche_count'] == 0:
        if 'Categorie' not in filtered_data.columns:
            missing_columns.append('Categorie')
        if 'Qtte' not in filtered_data.columns:
            missing_columns.append('Qtte')
    
    if metrics['retouche_rate'] == 0 and 'QtteSondee' not in filtered_data.columns:
        missing_columns.append('QtteSondee')
    
    if metrics['retouche_time'] == 0 and 'Temps' not in filtered_data.columns:
        missing_columns.append('Temps')
    
    if metrics['retouche_time_rate'] == 0 and 'QtteLct' not in filtered_data.columns:
        missing_columns.append('QtteLct')
    
    if metrics['retouche_cost'] == 0 and 'CoutMinute' not in filtered_data.columns:
        missing_columns.append('CoutMinute')
    
    # Check for rebut metrics
    if metrics['rebut_count'] == 0 and 'QtteLct' not in filtered_data.columns:
        if 'QtteLct' not in missing_columns:
            missing_columns.append('QtteLct')
    
    if metrics['rebut_cost'] == 0 and 'Prix' not in filtered_data.columns:
        missing_columns.append('Prix')
    
    # Check for penalite metrics
    if metrics['penalite'] == 0:
        if 'Penalite' not in filtered_data.columns and 'Type' not in filtered_data.columns:
            missing_columns.append('Penalite')
    
    # Display alerts for missing columns
    if missing_columns:
        st.markdown("### Données manquantes")
        for column in set(missing_columns):  # Use set to remove duplicates
            create_alert_notice(column)

# Create gauge chart for metrics
def create_gauge_chart(value, max_val, title, color_scheme='indigo'):
    """
    Create a gauge chart for displaying metrics
    
    Args:
        value: The value to display
        max_val: The maximum value for the gauge
        title: The title of the gauge
        color_scheme: Color scheme to use (indigo, emerald, amber)
        
    Returns:
        Plotly figure object
    """
    # Define color schemes
    color_schemes = {
        'indigo': ['#c7d2fe', '#a5b4fc', '#818cf8', '#6366f1', '#4f46e5'],
        'emerald': ['#a7f3d0', '#6ee7b7', '#34d399', '#10b981', '#059669'],
        'amber': ['#fde68a', '#fcd34d', '#fbbf24', '#f59e0b', '#d97706'],
        'rose': ['#fecdd3', '#fda4af', '#fb7185', '#f43f5e', '#e11d48']
    }
    
    colors = color_schemes.get(color_scheme, color_schemes['indigo'])
    
    # Calculate percentage for the gauge
    percentage = min(value / max_val, 1) * 100 if max_val > 0 else 0
    
    # Create the gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': '#f8fafc'}},
        gauge={
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "#f8fafc"},
            'bar': {'color': colors[3]},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'bordercolor': "rgba(0,0,0,0)",
            'steps': [
                {'range': [0, max_val * 0.2], 'color': colors[0]},
                {'range': [max_val * 0.2, max_val * 0.4], 'color': colors[1]},
                {'range': [max_val * 0.4, max_val * 0.6], 'color': colors[2]},
                {'range': [max_val * 0.6, max_val * 0.8], 'color': colors[3]},
                {'range': [max_val * 0.8, max_val], 'color': colors[4]}
            ],
        },
        number={'font': {'size': 24, 'color': '#f8fafc'}, 'suffix': " TND"},
    ))
    
    # Update layout for dark theme
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=60, b=10),
        height=300,
        font=dict(color='#f8fafc')
    )
    
    return fig

# Create tactical dashboard header
def create_tactical_header():
    st.markdown("""
    <div class="dashboard-header">
        <h1 class="dashboard-title">Dashboard Tactique</h1>
        <h3 class="dashboard-subtitle">Niveau chefs services</h3>
    </div>
    """, unsafe_allow_html=True)

def create_tactical_metrics(filtered_data):
    """
    Calculate tactical metrics with exact formulas as specified
    
    Args:
        filtered_data: DataFrame with production data
        
    Returns:
        Dictionary with all calculated metrics
    """
    metrics = {
        # Retouche Metrics
        'retouche_count': 0,
        'retouche_rate': 0,
        'retouche_time': 0,
        'retouche_time_rate': 0,
        'retouche_cost': 0,
        'retouche_cost_rate': 0,
        
        # Rebut Metrics
        'rebut_count': 0,
        'rebut_rate': 0,
        'rebut_cost': 0,
        'rebut_cost_rate': 0,
        
        # Penalité Metrics
        'penalite': 0,
        'penalite_rate': 0,
        
        # Technical
        'total_production_value': 0,
        'total_export_value': 0
    }

    # Helper function for safe division
    def safe_divide(a, b):
        return a / b if b != 0 else 0
    
    try:
        # Define default values for missing columns
        prix_unitaire = 100  # Default price per unit
        cout_minute = 0.5    # Default cost per minute
        
        # 1. RETOUCHE CALCULATIONS ========================================
        
        # Nbre de retouche = sum of column Qtte where categorie = "PRODUCTION FIN CHAINE"
        if 'Categorie' in filtered_data.columns and 'Qtte' in filtered_data.columns:
            fin_chaine_data = filtered_data[filtered_data['Categorie'] == 'PRODUCTION FIN CHAINE']
            metrics['retouche_count'] = fin_chaine_data['Qtte'].sum()
        else:
            metrics['retouche_count'] = 0
            
        # Taux de retouche = nbre de retouche / sum of column QtteSondee where categorie = "PRODUCTION FIN CHAINE"
        if 'Categorie' in filtered_data.columns and 'QtteSondee' in filtered_data.columns:
            fin_chaine_data = filtered_data[filtered_data['Categorie'] == 'PRODUCTION FIN CHAINE']
            total_sondee = fin_chaine_data['QtteSondee'].sum()
            metrics['retouche_rate'] = safe_divide(metrics['retouche_count'], total_sondee) * 100
        else:
            metrics['retouche_rate'] = 0
            
        # Temps de retouche totale = sum(nbre de retouche of the operation * Temps)
        # Convert hours to minutes as specified
        if 'Categorie' in filtered_data.columns and 'Qtte' in filtered_data.columns and 'Temps' in filtered_data.columns:
            fin_chaine_data = filtered_data[filtered_data['Categorie'] == 'PRODUCTION FIN CHAINE']
            # Assuming Temps is in hours, convert to minutes (multiply by 60)
            metrics['retouche_time'] = (fin_chaine_data['Qtte'] * fin_chaine_data['Temps'] * 60).sum()
        else:
            metrics['retouche_time'] = 0
            
        # Taux de temps de retouche = temps de retouche / somme(QtteLct de chaque gamme * prix unitaire)
        if 'QtteLct' in filtered_data.columns:
            # Use prix_unitaire as default if Prix column doesn't exist
            if 'Prix' in filtered_data.columns:
                total_value = (filtered_data['QtteLct'] * filtered_data['Prix']).sum()
            else:
                total_value = filtered_data['QtteLct'].sum() * prix_unitaire
                
            metrics['retouche_time_rate'] = safe_divide(metrics['retouche_time'], total_value) * 100
        else:
            metrics['retouche_time_rate'] = 0
            
        # Cout de retouche = sum(Qtte * Temps (in minutes) * cout mn)
        if 'Categorie' in filtered_data.columns and 'Qtte' in filtered_data.columns and 'Temps' in filtered_data.columns:
            fin_chaine_data = filtered_data[filtered_data['Categorie'] == 'PRODUCTION FIN CHAINE']
            # Use cout_minute as default if no specific column exists
            if 'CoutMinute' in filtered_data.columns:
                metrics['retouche_cost'] = (fin_chaine_data['Qtte'] * fin_chaine_data['Temps'] * 60 * fin_chaine_data['CoutMinute']).sum()
            else:
                metrics['retouche_cost'] = (fin_chaine_data['Qtte'] * fin_chaine_data['Temps'] * 60 * cout_minute).sum()
        else:
            metrics['retouche_cost'] = 0
            
        # %cout de retouche = cout de retouche / sum(QtteSondee * prix)
        if 'QtteSondee' in filtered_data.columns:
            # Use prix_unitaire as default if Prix column doesn't exist
            if 'Prix' in filtered_data.columns:
                total_value = (filtered_data['QtteSondee'] * filtered_data['Prix']).sum()
            else:
                total_value = filtered_data['QtteSondee'].sum() * prix_unitaire
                
            metrics['retouche_cost_rate'] = safe_divide(metrics['retouche_cost'], total_value) * 100
        else:
            metrics['retouche_cost_rate'] = 0
            
        # 2. REBUT CALCULATIONS ==========================================
        
        # Rebut = QtteLct – qté exportée (make it 10% of QtteLct)
        if 'QtteLct' in filtered_data.columns:
            total_lct = filtered_data['QtteLct'].sum()
            # Calculate rebut as 10% of QtteLct (since exported is 90%)
            metrics['rebut_count'] = total_lct * 0.1
        else:
            metrics['rebut_count'] = 0
            
        # Taux rebut = Rebut / sum(QtteLct)
        if 'QtteLct' in filtered_data.columns:
            total_lct = filtered_data['QtteLct'].sum()
            metrics['rebut_rate'] = safe_divide(metrics['rebut_count'], total_lct) * 100
        else:
            metrics['rebut_rate'] = 0
            
        # Coût rebut = sum(Rebut * prix_unitaire)
        if 'Prix' in filtered_data.columns:
            avg_price = filtered_data['Prix'].mean()
            metrics['rebut_cost'] = metrics['rebut_count'] * avg_price
        else:
            metrics['rebut_cost'] = metrics['rebut_count'] * prix_unitaire
            
        # Taux cout rebut = cout rebut / somme(qté exportée * prix unitaire)
        if 'QtteLct' in filtered_data.columns:
            # Exported quantity is 90% of QtteLct
            qte_exportee = filtered_data['QtteLct'].sum() * 0.9
            
            # Calculate total value of exported quantity
            if 'Prix' in filtered_data.columns:
                total_export_value = qte_exportee * filtered_data['Prix'].mean()
            else:
                total_export_value = qte_exportee * prix_unitaire
                
            metrics['rebut_cost_rate'] = safe_divide(metrics['rebut_cost'], total_export_value) * 100
            
            # Store these values for other calculations
            metrics['total_production_value'] = (filtered_data['QtteLct'].sum() * 
                                               (filtered_data['Prix'].mean() if 'Prix' in filtered_data.columns else prix_unitaire))
            metrics['total_export_value'] = total_export_value
        else:
            metrics['rebut_cost_rate'] = 0
            
        # 3. PENALITE CALCULATIONS ======================================
        # Calculate penalties based on available data
        if 'Penalite' in filtered_data.columns:
            metrics['penalite'] = filtered_data['Penalite'].sum()
        elif 'Type' in filtered_data.columns:
            # Assume penalties for certain defect types
            penalite_defauts = filtered_data[filtered_data['Type'].str.contains('DEFECT', case=False, na=False)]
            metrics['penalite'] = penalite_defauts['Qtte'].sum() * 10  # 10€ per defect for example
        
        # Calculate penalty rate
        if metrics['penalite'] > 0 and metrics['total_export_value'] > 0:
            metrics['penalite_rate'] = (metrics['penalite'] / metrics['total_export_value']) * 100

    except Exception as e:
        print(f"Error in calculation: {str(e)}")
        # In production, use an appropriate logging system

    return metrics

# Create top operations pie chart
def create_top_operations_pie(filtered_data, category_filter=None, n=3, title=None, color_scheme='indigo'):
    """
    Create a pie chart showing top operations
    
    Args:
        filtered_data: DataFrame with production data
        category_filter: Optional filter for category column
        n: Number of top items to show
        title: Chart title
        color_scheme: Color scheme to use
        
    Returns:
        Plotly figure object
    """
    # Define color schemes
    color_schemes = {
        'indigo': ['#c7d2fe', '#a5b4fc', '#818cf8', '#6366f1', '#4f46e5'],
        'emerald': ['#a7f3d0', '#6ee7b7', '#34d399', '#10b981', '#059669'],
        'amber': ['#fde68a', '#fcd34d', '#fbbf24', '#f59e0b', '#d97706'],
        'rose': ['#fecdd3', '#fda4af', '#fb7185', '#f43f5e', '#e11d48']
    }
    
    colors = color_schemes.get(color_scheme, color_schemes['indigo'])
    
    # Use IDOperation instead of operation
    if 'IDOperation' not in filtered_data.columns:
        # Fallback to sample data if column doesn't exist
        return px.pie(
            names=["No Data Available"],
            values=[1],
            title=title or f"Répartition Top {n} opérations",
            color_discrete_sequence=[colors[2]],
            hole=0.5
        )
    
    # Apply category filter if provided
    if category_filter and 'Categorie' in filtered_data.columns:
        data = filtered_data[filtered_data['Categorie'] == category_filter]
    else:
        data = filtered_data
    
    # Group by IDOperation and sum the Qtte value
    if 'Qtte' in data.columns:
        operation_data = data.groupby('IDOperation')['Qtte'].sum().reset_index()
    else:
        # If no Qtte column, count occurrences
        operation_data = data.groupby('IDOperation').size().reset_index(name='count')
        operation_data.rename(columns={'count': 'Qtte'}, inplace=True)
    
    # Sort and get top N operations
    operation_data = operation_data.sort_values('Qtte', ascending=False)
    
    # Handle empty data
    if len(operation_data) == 0:
        return px.pie(
            names=["No Data Available"],
            values=[1],
            title=title or f"Répartition Top {n} opérations",
            color_discrete_sequence=[colors[2]],
            hole=0.5
        )
    
    # Get top N operations
    top_operations = operation_data.head(n)
    
    # Calculate sum for "Other" category
    other_sum = operation_data[~operation_data['IDOperation'].isin(top_operations['IDOperation'])]['Qtte'].sum()
    
    # Add "Other" category if there are more operations
    if other_sum > 0:
        top_operations = pd.concat([
            top_operations,
            pd.DataFrame({'IDOperation': ['Autres'], 'Qtte': [other_sum]})
        ])
    
    # Create pie chart with improved design
    fig = px.pie(
        top_operations,
        names='IDOperation',
        values='Qtte',
        title=title or f"Répartition Top {n} opérations",
        color_discrete_sequence=colors,
        hole=0.5
    )
    
    # Update layout for dark theme with transparent background
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=40, b=10),
        height=300,
        font=dict(size=12, color='#f8fafc'),
        title_font=dict(size=16, color='#f8fafc'),
        legend=dict(
            font=dict(size=12, color='#f8fafc'),
            bgcolor='rgba(30,41,59,0.7)',
            bordercolor='rgba(30,41,59,0.7)'
        )
    )
    
    # Update traces for better visibility with transparent background
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont=dict(size=12, color='#ffffff'),
        marker=dict(line=dict(color='rgba(0,0,0,0)', width=1))
    )
    
    return fig

# Create top chains pie chart using the IDchainemontage column
def create_top_chains_pie(filtered_data, category_filter=None, n=3, title=None, color_scheme='emerald'):
    """
    Create a pie chart showing top chains
    
    Args:
        filtered_data: DataFrame with production data
        category_filter: Optional filter for category column
        n: Number of top items to show
        title: Chart title
        color_scheme: Color scheme to use
        
    Returns:
        Plotly figure object
    """
    # Define color schemes
    color_schemes = {
        'indigo': ['#c7d2fe', '#a5b4fc', '#818cf8', '#6366f1', '#4f46e5'],
        'emerald': ['#a7f3d0', '#6ee7b7', '#34d399', '#10b981', '#059669'],
        'amber': ['#fde68a', '#fcd34d', '#fbbf24', '#f59e0b', '#d97706'],
        'rose': ['#fecdd3', '#fda4af', '#fb7185', '#f43f5e', '#e11d48']
    }
    
    colors = color_schemes.get(color_scheme, color_schemes['emerald'])
    
    if 'IDchainemontage' not in filtered_data.columns and 'IDChaineMontage1' not in filtered_data.columns:
        # Fallback to sample data if column doesn't exist
        return px.pie(
            names=["No Data Available"],
            values=[1],
            title=title or f"Répartition Top {n} chaînes",
            color_discrete_sequence=[colors[2]],
            hole=0.5
        )
    
    # Use IDChaineMontage1 if available, otherwise use IDchainemontage
    chain_column = 'IDChaineMontage1' if 'IDChaineMontage1' in filtered_data.columns else 'IDchainemontage'
    
    # Apply category filter if provided
    if category_filter and 'Categorie' in filtered_data.columns:
        data = filtered_data[filtered_data['Categorie'] == category_filter]
    else:
        data = filtered_data
    
    # Group by chain and sum the Qtte value
    if 'Qtte' in data.columns:
        chain_data = data.groupby(chain_column)['Qtte'].sum().reset_index()
    else:
        # If no Qtte column, count occurrences
        chain_data = data.groupby(chain_column).size().reset_index(name='count')
        chain_data.rename(columns={'count': 'Qtte'}, inplace=True)
    
    # Sort and get top N chains
    chain_data = chain_data.sort_values('Qtte', ascending=False)
    
    # Handle empty data
    if len(chain_data) == 0:
        return px.pie(
            names=["No Data Available"],
            values=[1],
            title=title or f"Répartition Top {n} chaînes",
            color_discrete_sequence=[colors[2]],
            hole=0.5
        )
    
    # Get top N chains
    top_chains = chain_data.head(n)
    
    # Calculate sum for "Other" category
    other_sum = chain_data[~chain_data[chain_column].isin(top_chains[chain_column])]['Qtte'].sum()
    
    # Add "Other" category if there are more chains
    if other_sum > 0:
        top_chains = pd.concat([
            top_chains,
            pd.DataFrame({chain_column: ['Autres'], 'Qtte': [other_sum]})
        ])
    
    # Create pie chart with improved design
    fig = px.pie(
        top_chains,
        names=chain_column,
        values='Qtte',
        title=title or f"Répartition Top {n} chaînes",
        color_discrete_sequence=colors,
        hole=0.5
    )
    
    # Update layout for dark theme
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=40, b=10),
        height=300,
        font=dict(size=12, color='#f8fafc'),
        title_font=dict(size=16, color='#f8fafc'),
        legend=dict(
            font=dict(size=12, color='#f8fafc'),
            bgcolor='rgba(30,41,59,0.7)',
            bordercolor='rgba(30,41,59,0.7)'
        )
    )
    
    # Update traces for better visibility
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont=dict(size=12, color='#ffffff'),
        marker=dict(line=dict(color='rgba(0,0,0,0)', width=1))
    )
    
    return fig

# Create historical trend line chart
def create_trend_chart(filtered_data, category, group_by, title=None, color_scheme='indigo', top_n=5):
    """
    Create a line chart showing historical trends
    
    Args:
        filtered_data: DataFrame with production data
        category: Category to filter by
        group_by: Column to group by
        title: Chart title
        color_scheme: Color scheme to use
        top_n: Number of top items to show when grouping by IDOperation
        
    Returns:
        Plotly figure object
    """
    # Define color schemes
    color_schemes = {
        'indigo': ['#c7d2fe', '#a5b4fc', '#818cf8', '#6366f1', '#4f46e5'],
        'emerald': ['#a7f3d0', '#6ee7b7', '#34d399', '#10b981', '#059669'],
        'amber': ['#fde68a', '#fcd34d', '#fbbf24', '#f59e0b', '#d97706'],
        'rose': ['#fecdd3', '#fda4af', '#fb7185', '#f43f5e', '#e11d48']
    }
    
    colors = color_schemes.get(color_scheme, color_schemes['indigo'])
    
    if 'DATE' not in filtered_data.columns:
        # Fallback to empty chart if columns don't exist
        fig = go.Figure()
        fig.update_layout(
            title=title or f"Historique",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=40, b=10),
            height=250,
            font=dict(size=12, color='#f8fafc'),
            title_font=dict(size=16, color='#f8fafc')
        )
        fig.add_annotation(
            text="No data available",
            showarrow=False,
            font=dict(size=14, color='#f8fafc')
        )
        return fig
    
    # Convert date to monthly format
    filtered_data['Month'] = pd.to_datetime(filtered_data['DATE']).dt.strftime('%Y-%m')
    
    # Check if group_by exists in the dataframe
    if group_by and group_by in filtered_data.columns:
        # For IDOperation, limit to top N operations by total quantity
        if group_by == 'IDOperation':
            # Get the top N operations by total quantity
            if 'Qtte' in filtered_data.columns:
                top_operations = filtered_data.groupby(group_by)['Qtte'].sum().nlargest(top_n).index.tolist()
            else:
                # If no Qtte column, count occurrences
                top_operations = filtered_data.groupby(group_by).size().nlargest(top_n).index.tolist()
            
            # Filter data to only include top operations
            filtered_data = filtered_data[filtered_data[group_by].isin(top_operations)]
        
        # Group by month and the specified group_by column
        if 'Qtte' in filtered_data.columns:
            trend_data = filtered_data.groupby(['Month', group_by])['Qtte'].sum().reset_index()
        else:
            trend_data = filtered_data.groupby(['Month', group_by]).size().reset_index(name='Qtte')
        
        # Create line chart
        fig = px.line(
            trend_data,
            x='Month',
            y='Qtte',
            color=group_by,
            title=title or f"Historique par {group_by}" + (f" (Top {top_n})" if group_by == 'IDOperation' else ""),
            markers=True,
            color_discrete_sequence=colors
        )
    else:
        # Group by month only
        if 'Qtte' in filtered_data.columns:
            trend_data = filtered_data.groupby('Month')['Qtte'].sum().reset_index()
        else:
            trend_data = filtered_data.groupby('Month').size().reset_index(name='Qtte')
        
        # Create line chart
        fig = px.line(
            trend_data,
            x='Month',
            y='Qtte',
            title=title or "Historique",
            markers=True,
            line_shape='spline',
            color_discrete_sequence=[colors[2]]
        )
    
    # Add moving average
    window_size = 3 if len(trend_data['Month'].unique()) >= 3 else len(trend_data['Month'].unique())
    if window_size > 0 and not group_by:
        # Calculate moving average
        trend_data['MA'] = trend_data['Qtte'].rolling(window=window_size, min_periods=1).mean()
        
        # Add moving average line
        fig.add_scatter(
            x=trend_data['Month'],
            y=trend_data['MA'],
            mode='lines',
            name=f'Moyenne mobile sur {window_size}',
            line=dict(color='#f59e0b', width=2, dash='dot')
        )
    
    # Update layout for dark theme with transparent background
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=40, b=10),
        height=250,
        font=dict(size=12, color='#f8fafc'),
        title_font=dict(size=16, color='#f8fafc'),
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(size=10, color='#f8fafc'),
            bgcolor='rgba(30,41,59,0.7)',
            bordercolor='rgba(30,41,59,0.7)'
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(107,114,128,0.2)',
            tickfont=dict(color='#f8fafc'),
            title_font=dict(color='#f8fafc')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(107,114,128,0.2)',
            tickfont=dict(color='#f8fafc'),
            title_font=dict(color='#f8fafc')
        )
    )
    
    return fig

# Create custom metric display
def display_metric(label, value, unit="", tooltip=None):
    """
    Display a metric with custom styling
    
    Args:
        label: Metric label
        value: Metric value
        unit: Unit of measurement
        tooltip: Optional tooltip text
    """
    tooltip_html = ""
    if tooltip:
        tooltip_html = f"""
        <div class="tooltip">
            <span style="margin-left: 5px; font-size: 14px;">ℹ️</span>
            <span class="tooltiptext">{tooltip}</span>
        </div>
        """
    
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">{label}{tooltip_html}</div>
        <div class="metric-value">{value} {unit}</div>
    </div>
    """, unsafe_allow_html=True)

# Create section header
def create_section_header(title):
    """
    Create a section header with custom styling
    
    Args:
        title: Section title
    """
    st.markdown(f"""
    <div class="section-header">
        <h3 class="section-title">{title}</h3>
    </div>
    """, unsafe_allow_html=True)

# Create tactical dashboard layout
def create_tactical_dashboard(data):
    """
    Create the tactical dashboard layout
    
    Args:
        data: DataFrame with production data
    """
    # Apply dark theme
    apply_dark_theme()
    
    # Create header
    create_tactical_header()
    
    # Create simplified filters - only date
    st.markdown("""
    <div class="filter-container">
        <div class="filter-title">Filtres</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Date range filter
        start_date = st.date_input("Date de début", 
                                   value=pd.to_datetime(data['DATE'].min()) if 'DATE' in data.columns else None)
    
    with col2:
        # Date range filter
        end_date = st.date_input("Date de fin", 
                                value=pd.to_datetime(data['DATE'].max()) if 'DATE' in data.columns else None)
    
    # Apply date filter
    filtered_data = data.copy()
    if 'DATE' in filtered_data.columns:
        filtered_data = apply_date_filter(filtered_data, start_date, end_date)
    
    # Calculate metrics
    metrics = create_tactical_metrics(filtered_data)
    
    # Check for missing data and display alerts
    check_missing_data(filtered_data, metrics)
    
    # Create dashboard layout
    st.markdown("""
    <div class="divider"></div>
    """, unsafe_allow_html=True)
    
    # ---------------- RETOUCHE SECTION ----------------
    create_section_header("RETOUCHE")
    
    # First row of Retouche charts
    row1_cols = st.columns(2)
    
    # Top operations for Retouche
    with row1_cols[0]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:10px; color:#f8fafc;">Top 3 opérations - Retouche</h4>
        """, unsafe_allow_html=True)
        
        if 'IDOperation' not in filtered_data.columns:
            create_alert_notice("IDOperation")
        
        operations_pie = create_top_operations_pie(
            filtered_data, 
            category_filter="PRODUCTION FIN CHAINE", 
            n=3, 
            title="",
            color_scheme='indigo'
        )
        st.plotly_chart(operations_pie, use_container_width=True, key="retouche_operations_pie")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Cost gauge for Retouche
    with row1_cols[1]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:10px; color:#f8fafc;">Coût Retouche Cumulé</h4>
        """, unsafe_allow_html=True)
        
        if metrics['retouche_cost'] == 0:
            if 'Temps' not in filtered_data.columns:
                create_alert_notice("Temps")
            if 'CoutMinute' not in filtered_data.columns:
                create_alert_notice("CoutMinute")
        
        # Set a target value for max
        if 'Quantite' in filtered_data.columns:
            total_value = filtered_data['Quantite'].sum() * 100  # Assume 100€ per unit
            max_acceptable_cost = total_value * 0.05  # 5% of total value as maximum acceptable cost
        else:
            # Fallback to a reasonable multiple of current cost
            max_acceptable_cost = max(10000, metrics["retouche_cost"] * 2)
        
        retouche_gauge = create_gauge_chart(
            value=metrics["retouche_cost"],
            max_val=max_acceptable_cost,
            title="",
            color_scheme='indigo'
        )
        st.plotly_chart(retouche_gauge, use_container_width=True, key="retouche_gauge_chart")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Second row of Retouche charts
    row2_cols = st.columns(2)
    
    # Top chains for Retouche
    with row2_cols[0]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:10px; color:#f8fafc;">Top 3 chaînes - Retouche</h4>
        """, unsafe_allow_html=True)
        
        if 'IDchainemontage' not in filtered_data.columns and 'IDChaineMontage1' not in filtered_data.columns:
            create_alert_notice("IDchainemontage ou IDChaineMontage1")
        
        chains_pie = create_top_chains_pie(
            filtered_data, 
            category_filter="PRODUCTION FIN CHAINE", 
            n=3, 
            title=""
        )
        st.plotly_chart(chains_pie, use_container_width=True, key="retouche_chains_pie")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Retouche metrics
    with row2_cols[1]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:15px; color:#f8fafc;">Métriques Retouche</h4>
        """, unsafe_allow_html=True)
        
        metrics_cols = st.columns(2)
        
        with metrics_cols[0]:
            display_metric("Nombre de retouche", f"{metrics['retouche_count']:,.0f}", "pcs", 
                          "Nombre total de retouches dans la période sélectionnée")
            if metrics['retouche_count'] == 0:
                if 'Categorie' not in filtered_data.columns:
                    create_alert_notice("Categorie")
                if 'Qtte' not in filtered_data.columns:
                    create_alert_notice("Qtte")
                
            display_metric("Temps de retouche", f"{metrics['retouche_time']:,.0f}", "min", 
                          "Temps total passé en retouche (en minutes)")
            if metrics['retouche_time'] == 0 and 'Temps' not in filtered_data.columns:
                create_alert_notice("Temps")
                
            display_metric("Coût de retouche", f"{metrics['retouche_cost']:,.0f}", "TND", 
                          "Coût total des retouches")
        
        with metrics_cols[1]:
            display_metric("Taux de retouche", f"{metrics['retouche_rate']:.2f}", "%", 
                          "Pourcentage de produits retouchés")
            if metrics['retouche_rate'] == 0 and 'QtteSondee' not in filtered_data.columns:
                create_alert_notice("QtteSondee")
                
            display_metric("Taux temps retouche", f"{metrics['retouche_time_rate']:.2f}", "%", 
                          "Pourcentage du temps passé en retouche")
            if metrics['retouche_time_rate'] == 0 and 'QtteLct' not in filtered_data.columns:
                create_alert_notice("QtteLct")
                
            display_metric("% coût de retouche", f"{metrics['retouche_cost_rate']:.2f}", "%", 
                          "Pourcentage du coût total représenté par les retouches")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Add spacer between sections
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # ---------------- REBUT SECTION ----------------
    create_section_header("REBUT")
    
    # First row of Rebut charts
    row3_cols = st.columns(2)
    
    # Top operations for Rebut
    with row3_cols[0]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:10px; color:#f8fafc;">Top 3 opérations - Rebut</h4>
        """, unsafe_allow_html=True)
        
        if 'IDOperation' not in filtered_data.columns:
            create_alert_notice("IDOperation")
        
        operations_pie = create_top_operations_pie(
            filtered_data, 
            n=3, 
            title="",
            color_scheme='rose'
        )
        st.plotly_chart(operations_pie, use_container_width=True, key="rebut_operations_pie")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Cost gauge for Rebut
    with row3_cols[1]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:10px; color:#f8fafc;">Coût Rebut Cumulé</h4>
        """, unsafe_allow_html=True)
        
        if metrics['rebut_cost'] == 0:
            if 'QtteLct' not in filtered_data.columns:
                create_alert_notice("QtteLct")
            if 'Prix' not in filtered_data.columns:
                create_alert_notice("Prix")
        
        # Set a target value for max
        if 'Quantite' in filtered_data.columns:
            total_value = filtered_data['Quantite'].sum() * 100  # Assume 100€ per unit
            max_acceptable_cost = total_value * 0.05  # 5% of total value as maximum acceptable cost
        else:
            # Fallback to a reasonable multiple of current cost
            max_acceptable_cost = max(10000, metrics["rebut_cost"] * 2)
        
        rebut_gauge = create_gauge_chart(
            value=metrics["rebut_cost"],
            max_val=max_acceptable_cost,
            title="",
            color_scheme='rose'
        )
        st.plotly_chart(rebut_gauge, use_container_width=True, key="rebut_gauge_chart")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Second row of Rebut charts
    row4_cols = st.columns(2)
    
    # Top chains for Rebut
    with row4_cols[0]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:10px; color:#f8fafc;">Top 3 chaînes - Rebut</h4>
        """, unsafe_allow_html=True)
        
        if 'IDchainemontage' not in filtered_data.columns and 'IDChaineMontage1' not in filtered_data.columns:
            create_alert_notice("IDchainemontage ou IDChaineMontage1")
        
        chains_pie = create_top_chains_pie(
            filtered_data, 
            n=3, 
            title="",
            color_scheme='emerald'
        )
        st.plotly_chart(chains_pie, use_container_width=True, key="rebut_chains_pie")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Rebut metrics
    with row4_cols[1]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:15px; color:#f8fafc;">Métriques Rebut</h4>
        """, unsafe_allow_html=True)
        
        metrics_cols = st.columns(2)
        
        with metrics_cols[0]:
            display_metric("Rebut", f"{metrics['rebut_count']:,.0f}", "pcs", 
                          "Nombre total de produits rebutés")
            if metrics['rebut_count'] == 0 and 'QtteLct' not in filtered_data.columns:
                create_alert_notice("QtteLct")
                
            display_metric("Coût rebut", f"{metrics['rebut_cost']:,.0f}", "TND", 
                          "Coût total des rebuts")
        
        with metrics_cols[1]:
            display_metric("Taux rebut", f"{metrics['rebut_rate']:.2f}", "%", 
                          "Pourcentage de produits rebutés")
            display_metric("Taux coût de rebut", f"{metrics['rebut_cost_rate']:.2f}", "%", 
                          "Pourcentage du coût total représenté par les rebuts")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Add spacer between sections
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # ---------------- PENALITE SECTION ----------------
    create_section_header("PÉNALITÉ")
    
    # First row of Penalty charts
    row5_cols = st.columns(2)
    
    # Penalty metrics
    with row5_cols[0]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:15px; color:#f8fafc;">Métriques Pénalité</h4>
        """, unsafe_allow_html=True)
        
        metrics_cols = st.columns(2)
        
        with metrics_cols[0]:
            display_metric("Pénalité qualité", f"{metrics['penalite']:,.0f}", "TND", 
                          "Montant total des pénalités qualité")
            if metrics['penalite'] == 0:
                if 'Penalite' not in filtered_data.columns and 'Type' not in filtered_data.columns:
                    create_alert_notice("Penalite")
        
        with metrics_cols[1]:
            display_metric("Taux Pénalité qualité", f"{metrics['penalite_rate']:.2f}", "%", 
                          "Pourcentage du coût total représenté par les pénalités")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Cost gauge for Penalty
    with row5_cols[1]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:10px; color:#f8fafc;">Pénalités Cumulées</h4>
        """, unsafe_allow_html=True)
        
        # Set a target value for max
        if 'Quantite' in filtered_data.columns:
            total_value = filtered_data['Quantite'].sum() * 100  # Assume 100€ per unit
            max_acceptable_cost = total_value * 0.02  # 2% of total value as maximum acceptable cost
        else:
            # Fallback to a reasonable multiple of current cost
            max_acceptable_cost = max(5000, metrics["penalite"] * 2)
        
        penalty_gauge = create_gauge_chart(
            value=metrics["penalite"],
            max_val=max_acceptable_cost,
            title="",
            color_scheme='amber'
        )
        st.plotly_chart(penalty_gauge, use_container_width=True, key="penalite_gauge_chart")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Second row of Penalty charts
    row6_cols = st.columns(2)
    
    # Top operations for Penalty
    with row6_cols[0]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:10px; color:#f8fafc;">Top 3 opérations - Pénalité</h4>
        """, unsafe_allow_html=True)
        
        if 'IDOperation' not in filtered_data.columns:
            create_alert_notice("IDOperation")
        
        operations_pie = create_top_operations_pie(
            filtered_data, 
            n=3, 
            title="",
            color_scheme='amber'
        )
        st.plotly_chart(operations_pie, use_container_width=True, key="penalite_operations_pie")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with row6_cols[1]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:10px; color:#f8fafc;">Historique Pénalités</h4>
        """, unsafe_allow_html=True)
        
        penalty_trend = create_trend_chart(
            filtered_data, 
            'Penalite', 
            None, 
            title="",
            color_scheme='amber'
        )
        st.plotly_chart(penalty_trend, use_container_width=True, key="penalite_trend_chart")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Add spacer between sections
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # ---------------- TENDANCES HISTORIQUES SECTION ----------------
    create_section_header("TENDANCES HISTORIQUES")
    
    hist_cols = st.columns(2)
    
    # Historical trends for Retouche
    with hist_cols[0]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:10px; color:#f8fafc;">Historique Retouche par Opération</h4>
        """, unsafe_allow_html=True)
        
        if 'IDOperation' not in filtered_data.columns:
            create_alert_notice("IDOperation")
        
        defect_trend = create_trend_chart(
            filtered_data, 
            'Retouche', 
            'IDOperation', 
            title="",
            color_scheme='indigo'
        )
        st.plotly_chart(defect_trend, use_container_width=True, key="retouche_defect_trend")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with hist_cols[1]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:10px; color:#f8fafc;">Historique Retouche par Chaîne</h4>
        """, unsafe_allow_html=True)
        
        chain_column = 'IDChaineMontage1' if 'IDChaineMontage1' in filtered_data.columns else 'IDchainemontage'
        if chain_column not in filtered_data.columns:
            create_alert_notice("IDchainemontage ou IDChaineMontage1")
        
        provider_trend = create_trend_chart(
            filtered_data, 
            'Retouche', 
            chain_column, 
            title="",
            color_scheme='emerald'
        )
        st.plotly_chart(provider_trend, use_container_width=True, key="retouche_provider_trend")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Historical trends for Rebut
    hist_cols2 = st.columns(2)
    
    with hist_cols2[0]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:10px; color:#f8fafc;">Historique Rebut par Opération</h4>
        """, unsafe_allow_html=True)
        
        if 'IDOperation' not in filtered_data.columns:
            create_alert_notice("IDOperation")
        
        defect_trend = create_trend_chart(
            filtered_data, 
            'Rebut', 
            'IDOperation', 
            title="",
            color_scheme='rose'
        )
        st.plotly_chart(defect_trend, use_container_width=True, key="rebut_defect_trend")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with hist_cols2[1]:
        st.markdown("""
        <div class="card-container">
            <h4 style="margin-top:0; margin-bottom:10px; color:#f8fafc;">Historique Rebut par Chaîne</h4>
        """, unsafe_allow_html=True)
        
        chain_column = 'IDChaineMontage1' if 'IDChaineMontage1' in filtered_data.columns else 'IDchainemontage'
        if chain_column not in filtered_data.columns:
            create_alert_notice("IDchainemontage ou IDChaineMontage1")
        
        provider_trend = create_trend_chart(
            filtered_data, 
            'Rebut', 
            chain_column, 
            title="",
            color_scheme='emerald'
        )
        st.plotly_chart(provider_trend, use_container_width=True, key="rebut_provider_trend")
        st.markdown("</div>", unsafe_allow_html=True)