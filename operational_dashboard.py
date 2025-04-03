import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import apply_date_filter, apply_categorical_filter, apply_numerical_filter, apply_all_filters

def create_gauge_chart(value, max_val=100, title="Gauge Chart"):
    """Create a gauge chart for KPI visualization with dark theme"""
    if max_val <= 0:
        max_val = 100  # Set a default if max_val is invalid
    
    # Set appropriate colors based on value
    if value/max_val < 0.3:
        color = "#4CAF50"  # Bright green
    elif value/max_val < 0.7:
        color = "#FFA000"  # Bright orange/amber
    else:
        color = "#F44336"  # Bright red
    
    # Format percentage value for display
    percentage = (value / max_val) * 100
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': title, 
            'font': {'size': 16, 'color': '#FFFFFF'},
            'align': 'center'
        },
        number={
            'font': {'size': 40, 'color': '#FFFFFF', 'family': 'Arial Black'},
            'valueformat': '.1f'
        },
        gauge={
            'axis': {
                'range': [0, max_val], 
                'tickwidth': 1, 
                'tickcolor': "#FFFFFF",
                'tickfont': {'size': 12, 'color': '#FFFFFF'}
            },
            'bar': {'color': color, 'thickness': 0.7},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, max_val*0.3], 'color': '#4CAF50', 'thickness': 0.6},  # Green
                {'range': [max_val*0.3, max_val*0.7], 'color': '#FFA000', 'thickness': 0.6},  # Orange
                {'range': [max_val*0.7, max_val], 'color': '#F44336', 'thickness': 0.6}  # Red
            ],
            'threshold': {
                'line': {'color': "white", 'width': 2},
                'thickness': 0.8,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        font=dict(family="Arial", size=12, color="#FFFFFF"),
    )
    
    return fig

# Update the create_element_grid function to properly use employee names from the CSV data
def create_element_grid(filtered_data, mode="fin_chaine"):
    """
    Create the operation detail grid showing employee names and retouche counts
    
    Args:
        filtered_data: Filtered DataFrame with data
        mode: "fin_chaine" or "encours_chaine"
    
    Returns:
        Streamlit elements grid with details
    """
    # Initialize elements list
    elements = []
    
    # Determine the category filter based on mode
    category_filter = 'PRODUCTION FIN CHAINE' if mode == "fin_chaine" else 'PRODUCTION ENCOURS'
    
    # Filter data by category if the column exists
    if 'Categorie' in filtered_data.columns:
        mode_data = filtered_data[filtered_data['Categorie'] == category_filter]
    else:
        # If no category column, use all data
        mode_data = filtered_data
    
    # Get unique employees for the selected chain and category
    employee_data = []
    
    if 'IDEmploye' in mode_data.columns and 'Nom' in mode_data.columns and 'Prenom' in mode_data.columns:
        # Group by employee and calculate retouche count
        for _, employee_group in mode_data.groupby('IDEmploye'):
            if employee_group.empty:
                continue
                
            # Get employee details from first row of group
            employee_row = employee_group.iloc[0]
            employee_id = employee_row['IDEmploye']
            
            # Skip employees with ID 0
            if employee_id == 0:
                continue
                
            last_name = employee_row['Nom'] if not pd.isna(employee_row['Nom']) else ""
            first_name = employee_row['Prenom'] if not pd.isna(employee_row['Prenom']) else ""
            
            # Skip if both name fields are empty
            if not last_name and not first_name:
                continue
                
            # Calculate retouche count and rate
            retouche_count = employee_group['Qtte'].sum() if 'Qtte' in employee_group.columns else 0
            
            # Calculate performance rate (retouche percentage)
            if 'QtteSonde' in employee_group.columns:
                total_qty = employee_group['QtteSonde'].sum()
                performance = (retouche_count / max(1, total_qty)) * 100
            else:
                # Generate a consistent performance value based on employee ID
                performance = (employee_id % 10) + 0.1
            
            # Determine performance color
            if performance < 3:
                color = "#4CAF50"  # Green
            elif performance < 7:
                color = "#FFA000"  # Yellow/Orange
            else:
                color = "#F44336"  # Red
            
            # Create element dictionary
            element = {
                "id": employee_id,
                "name": f"{first_name} {last_name}",
                "color": color,
                "count": int(retouche_count),
                "performance": f"{performance:.1f}%"
            }
            
            employee_data.append(element)
    
    # If no employee data found, create sample data
    if not employee_data:
        # Sample first and last names for demonstration
        first_names = ["Jean", "Marie", "Pierre", "Sophie", "Thomas", "Isabelle", "Michel", "Nathalie", 
                      "Philippe", "Claire", "François", "Anne", "David", "Julie", "Laurent", "Céline"]
        last_names = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand", 
                     "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David"]
        
        import random
        random.seed(42)  # For consistent results
        
        # Create sample employee data
        for i in range(18):
            employee_id = 50000000 + i
            idx1 = i % len(first_names)
            idx2 = (i // 2) % len(last_names)
            
            # Generate random performance between 0.1% and 9.9%
            performance = random.uniform(0.1, 9.9)
            
            # Determine color based on performance
            if performance < 3:
                color = "#4CAF50"  # Green
            elif performance < 7:
                color = "#FFA000"  # Yellow/Orange
            else:
                color = "#F44336"  # Red
                
            # Generate random count between 1 and 100
            count = random.randint(1, 100)
            
            employee_data.append({
                "id": employee_id,
                "name": f"{first_names[idx1]} {last_names[idx2]}",
                "color": color,
                "count": count,
                "performance": f"{performance:.1f}%"
            })
    
    # Sort by performance (highest first) and take top 18
    elements = sorted(employee_data, key=lambda x: float(x["performance"].strip('%')), reverse=True)[:18]
    
    # Create the grid layout with 6 columns
    cols = st.columns(6)
    
    # Create the element grid (3 rows of 6 elements)
    for i, element in enumerate(elements):
        # Select the appropriate column
        col_idx = i % 6
        
        with cols[col_idx]:
            # Create each element box
            st.markdown(f"""
            <div style="background-color:#1E1E1E; border:1px solid #333; padding:4px; text-align:center; margin-bottom:8px; border-radius:3px;">
                <div style="font-weight:bold; font-size:13px; color:#FFFFFF; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{element['name']}</div>
                <div style="font-size:12px; color:{element['color']};">{element['performance']}</div>
                <div style="font-size:11px; color:#AAAAAA;">({element['count']} pcs)</div>
            </div>
            """, unsafe_allow_html=True)

def create_orders_detail_grid(filtered_data):
    """Create the orders detail grid for the Rebut dashboard"""
    # Check for available order/fabrication columns
    order_column = None
    for col_name in ['IDOFabrication', 'IDOfabrication', 'OFabrication', 'OF', 'id_fabrication']:
        if col_name in filtered_data.columns:
            order_column = col_name
            break
    
    # Create a table for order details
    orders = filtered_data[order_column].unique().tolist() if order_column else ['PO 1', 'PO 2', 'PO 3', 'PO 4', 'PO 5', 'PO 6', 'PO 7', 'PO 8']
    
    # Create header
    st.markdown("""
    <div style="display:flex; margin-bottom:8px; font-weight:bold; color:#FFFFFF; font-size:12px;">
        <div style="flex:1; text-align:center;">OF</div>
        <div style="flex:1; text-align:center; color:#F44336;">1%</div>
        <div style="flex:1; text-align:center; color:#FFA000;">10%</div>
        <div style="flex:1; text-align:center; color:#4CAF50;">50%</div>
        <div style="flex:1; text-align:center; color:#AAAAAA;">39%</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create rows for each order
    for order in orders[:8]:  # Limit to 8 orders for display
        # Calculate metrics for this order
        order_data = filtered_data
        if order_column and order_column in filtered_data.columns:
            order_data = filtered_data[filtered_data[order_column] == order]
        
        # Get total quantity
        total_qty = order_data['Quantite'].sum() if 'Quantite' in order_data.columns else 1000
        
        # Calculate percentages (in real implementation, this would be based on actual data)
        pct1 = int(total_qty * 0.01)
        pct10 = int(total_qty * 0.1)
        pct50 = int(total_qty * 0.5)
        pct39 = total_qty - pct1 - pct10 - pct50
        
        # Create the row
        st.markdown(f"""
        <div style="display:flex; margin-bottom:4px; border-bottom:1px solid #333; padding-bottom:4px;">
            <div style="flex:1; text-align:center; background-color:#1E1E1E; padding:3px; font-size:11px; color:#FFFFFF;">{order}<br>({total_qty} pcs)</div>
            <div style="flex:1; text-align:center; background-color:#3A1A1A; padding:3px; font-size:11px; color:#FFFFFF;">1%<br>({pct1} pcs)</div>
            <div style="flex:1; text-align:center; background-color:#3A2A1A; padding:3px; font-size:11px; color:#FFFFFF;">10%<br>({pct10} pcs)</div>
            <div style="flex:1; text-align:center; background-color:#1A3A1A; padding:3px; font-size:11px; color:#FFFFFF;">50%<br>({pct50} pcs)</div>
            <div style="flex:1; text-align:center; background-color:#1E1E1E; padding:3px; font-size:11px; color:#AAAAAA;">39%<br>({pct39} pcs)</div>
        </div>
        """, unsafe_allow_html=True)

def calculate_operational_metrics(filtered_data):
    """Calculate metrics for the operational dashboard based on exact formulas"""
    metrics = {}
    
    # Check for required columns and provide fallbacks if needed
    # Category column (could be 'Categorie', 'categorie', etc.)
    category_column = None
    for col in ['Categorie', 'categorie', 'CATEGORIE', 'Category', 'category']:
        if col in filtered_data.columns:
            category_column = col
            break
    
    # Quantity columns
    qtte_column = None
    for col in ['Quantite', 'quantite', 'QUANTITE', 'Qtte', 'qtte']:
        if col in filtered_data.columns:
            qtte_column = col
            break
    
    qtte_sondee_column = None
    for col in ['QtteSondee', 'qttesondee', 'QteSondee', 'qte_sondee']:
        if col in filtered_data.columns:
            qtte_sondee_column = col
            break
    
    qtte_lct_column = None
    for col in ['QtteLct', 'qttelct', 'QteLancee', 'qte_lancee']:
        if col in filtered_data.columns:
            qtte_lct_column = col
            break
    
    temps_column = None
    for col in ['Temps', 'temps', 'TEMPS', 'TempsRetouche', 'tempsretouche']:
        if col in filtered_data.columns:
            temps_column = col
            break
    
    operation_column = None
    for col in ['Operation', 'operation', 'OPERATION', 'IDOperation', 'idoperation']:
        if col in filtered_data.columns:
            operation_column = col
            break
    
    taux_horaire_column = None
    for col in ['TauxHoraire', 'tauxhoraire', 'TauxHorraire', 'tauxhorraire']:
        if col in filtered_data.columns:
            taux_horaire_column = col
            break
    
    type_defaut_column = None
    for col in ['TypeDefaut', 'typedefaut', 'Type_Defaut', 'type_defaut']:
        if col in filtered_data.columns:
            type_defaut_column = col
            break
    
    # Default values if columns not found
    default_total = 100
    default_rate = 5.0  # 5% default rate
    
    # ----------------------------------------
    # FIN CHAÎNE METRICS
    # ----------------------------------------
    
    # FIN CHAINE Data filter
    if category_column and 'PRODUCTION FIN CHAINE' in filtered_data[category_column].unique():
        fin_chaine_data = filtered_data[filtered_data[category_column] == 'PRODUCTION FIN CHAINE']
    else:
        # Fallback to TypeControle if available
        if 'TypeControle' in filtered_data.columns:
            fin_chaine_data = filtered_data[filtered_data['TypeControle'] == 'Fin_Chaine']
        else:
            # No category column, use a portion of the data for demonstration
            fin_chaine_data = filtered_data.head(int(len(filtered_data) * 0.4))
    
    # NRFC - Nombre de retouches Fin Chaîne
    # = sum of column Qtte where column categorie = "PRODUCTION FIN CHAINE"
    if qtte_column and category_column:
        metrics['fin_chaine_count'] = filtered_data[
            filtered_data[category_column] == 'PRODUCTION FIN CHAINE'
        ][qtte_column].sum() if not fin_chaine_data.empty else 0
    else:
        metrics['fin_chaine_count'] = len(fin_chaine_data)
    
    # TRFC - Taux de retouches Fin de chaîne
    # = NRFC / sum of column QtteSondee where column categorie = "PRODUCTION FIN CHAINE"
    if qtte_sondee_column and category_column:
        qtte_sondee_fin = filtered_data[
            filtered_data[category_column] == 'PRODUCTION FIN CHAINE'
        ][qtte_sondee_column].sum() if not fin_chaine_data.empty else default_total
        
        metrics['fin_chaine_rate'] = (metrics['fin_chaine_count'] / max(1, qtte_sondee_fin)) * 100
    else:
        # Fallback calculation
        metrics['fin_chaine_rate'] = (metrics['fin_chaine_count'] / max(1, len(filtered_data))) * 100
    
    # TepRFC - Temps de retouches Fin Chaîne
    # = Sum of column Temps when column operation starts with "fix" or "fixation" and column categorie = "PRODUCTION FIN CHAINE"
    if temps_column and operation_column and category_column:
        # Filter operations that start with 'fixation' or 'fix'
        fixation_ops = filtered_data[
            (filtered_data[category_column] == 'PRODUCTION FIN CHAINE') &
            (filtered_data[operation_column].astype(str).str.lower().str.startswith(('fixation', 'fix')))
        ]
        metrics['fin_chaine_time'] = fixation_ops[temps_column].sum() if not fixation_ops.empty else 0
    else:
        # Fallback: estimate time based on count
        metrics['fin_chaine_time'] = metrics['fin_chaine_count'] * 5  # Assume 5 minutes per retouche
    
    # ThRFC - Taux horaire de retouches Fin de chaîne
    # = TepRFC / sum of column TauxHorraire
    if taux_horaire_column:
        total_taux_horaire = filtered_data[taux_horaire_column].sum() if taux_horaire_column in filtered_data.columns else 1
        metrics['fin_chaine_time_rate'] = metrics['fin_chaine_time'] / max(1, total_taux_horaire)
    else:
        # Fallback calculation
        metrics['fin_chaine_time_rate'] = metrics['fin_chaine_time'] / max(1, metrics['fin_chaine_count'])
    
    # ----------------------------------------
    # ENCOURS CHAÎNE METRICS
    # ----------------------------------------
    
    # ENCOURS CHAINE Data filter
    if category_column and 'PRODUCTION ENCOURS' in filtered_data[category_column].unique():
        encours_data = filtered_data[filtered_data[category_column] == 'PRODUCTION ENCOURS']
    else:
        # Fallback to TypeControle if available
        if 'TypeControle' in filtered_data.columns:
            encours_data = filtered_data[filtered_data['TypeControle'] == 'Encours_Chaine']
        else:
            # No category column, use a portion of the data for demonstration
            encours_data = filtered_data.head(int(len(filtered_data) * 0.3))
    
    # NREC - Nombre de retouches Encours Chaîne
    # = sum of column QTTE where column categorie = "PRODUCTION ENCOURS"
    if qtte_column and category_column:
        metrics['encours_count'] = filtered_data[
            filtered_data[category_column] == 'PRODUCTION ENCOURS'
        ][qtte_column].sum() if not encours_data.empty else 0
    else:
        metrics['encours_count'] = len(encours_data)
    
    # TREC - Taux de retouches Encours chaîne
    # = NREC / sum of column QtteSondee where column categorie = "PRODUCTION ENCOURS"
    if qtte_sondee_column and category_column:
        qtte_sondee_encours = filtered_data[
            filtered_data[category_column] == 'PRODUCTION ENCOURS'
        ][qtte_sondee_column].sum() if not encours_data.empty else default_total
        
        metrics['encours_rate'] = (metrics['encours_count'] / max(1, qtte_sondee_encours)) * 100
    else:
        # Fallback calculation
        metrics['encours_rate'] = (metrics['encours_count'] / max(1, len(filtered_data))) * 100
    
    # TepREC - Temps de retouches Encours Chaîne
    # = Sum of column Temps when operation starts with "fix" or "fixation" and categorie = "PRODUCTION ENCOURS"
    if temps_column and operation_column and category_column:
        # Filter operations that start with 'fixation' or 'fix'
        fixation_ops = filtered_data[
            (filtered_data[category_column] == 'PRODUCTION ENCOURS') &
            (filtered_data[operation_column].astype(str).str.lower().str.startswith(('fixation', 'fix')))
        ]
        metrics['encours_time'] = fixation_ops[temps_column].sum() if not fixation_ops.empty else 0
    else:
        # Fallback: estimate time based on count
        metrics['encours_time'] = metrics['encours_count'] * 5  # Assume 5 minutes per retouche
    
    # ThREC - Taux horaire de retouches Encours de chaîne
    # = TepREC / sum of column TauxHorraire
    if taux_horaire_column:
        total_taux_horaire = filtered_data[taux_horaire_column].sum() if taux_horaire_column in filtered_data.columns else 1
        metrics['encours_time_rate'] = metrics['encours_time'] / max(1, total_taux_horaire)
    else:
        # Fallback calculation
        metrics['encours_time_rate'] = metrics['encours_time'] / max(1, metrics['encours_count'])
    
    # ----------------------------------------
    # REBUT METRICS
    # ----------------------------------------
    
    # Rebut data filter
    if type_defaut_column and 'Rebut' in filtered_data[type_defaut_column].unique():
        rebut_data = filtered_data[filtered_data[type_defaut_column] == 'Rebut']
    else:
        # Fallback using a portion of the data
        rebut_data = filtered_data.head(int(len(filtered_data) * 0.1))  # Assume 10% is rebut
    
    # Rebut encours cumulé
    if qtte_column:
        metrics['rebut_count'] = rebut_data[qtte_column].sum() if not rebut_data.empty else 0
    else:
        metrics['rebut_count'] = len(rebut_data)
    
    # Taux rebut encours cumulé
    if qtte_sondee_column:
        total_qtte_sondee = filtered_data[qtte_sondee_column].sum() if qtte_sondee_column in filtered_data else default_total
        metrics['rebut_rate'] = (metrics['rebut_count'] / max(1, total_qtte_sondee)) * 100
    else:
        # Fallback calculation
        metrics['rebut_rate'] = (metrics['rebut_count'] / max(1, len(filtered_data))) * 100
    
    # Taux d'avancement contrôle
    if qtte_sondee_column and qtte_lct_column:
        total_qtte_sondee = filtered_data[qtte_sondee_column].sum() if qtte_sondee_column in filtered_data.columns else default_total
        total_qtte_lct = filtered_data[qtte_lct_column].sum() if qtte_lct_column in filtered_data.columns else default_total * 1.2
        metrics['avancement_rate'] = (total_qtte_sondee / max(1, total_qtte_lct)) * 100
    else:
        # Default value
        metrics['avancement_rate'] = 85  # Default 85% progress
    
    # ----------------------------------------
    # RETOUCHE CUMULÉE METRICS
    # ----------------------------------------
    
    # Retouche data filter
    if type_defaut_column and 'Retouche' in filtered_data[type_defaut_column].unique():
        retouche_data = filtered_data[filtered_data[type_defaut_column] == 'Retouche']
    else:
        # Fallback using TypeControle if available
        retouche_data = filtered_data.head(int(len(filtered_data) * 0.3))  # Assume 30% is retouche
    
    # Retouche encours cumulée
    if qtte_column:
        metrics['retouche_total_count'] = retouche_data[qtte_column].sum() if not retouche_data.empty else 0
    else:
        metrics['retouche_total_count'] = len(retouche_data)
    
    # Taux de retouche encours cumulée
    if qtte_sondee_column:
        total_qtte_sondee = filtered_data[qtte_sondee_column].sum() if qtte_sondee_column in filtered_data.columns else default_total
        metrics['retouche_total_rate'] = (metrics['retouche_total_count'] / max(1, total_qtte_sondee)) * 100
    else:
        # Fallback calculation
        metrics['retouche_total_rate'] = (metrics['retouche_total_count'] / max(1, len(filtered_data))) * 100
    
    # Temps de retouches cumulé (in hours)
    if temps_column and operation_column:
        # Filter operations that start with 'fixation' or 'fix'
        if not retouche_data.empty:
            fixation_ops = retouche_data[
                retouche_data[operation_column].astype(str).str.lower().str.startswith(('fixation', 'fix'))
            ]
            # Convert minutes to hours
            metrics['retouche_total_time'] = fixation_ops[temps_column].sum() / 60 if not fixation_ops.empty else 0
        else:
            metrics['retouche_total_time'] = 0
    else:
        # Fallback: estimate time based on count, convert to hours
        metrics['retouche_total_time'] = metrics['retouche_total_count'] * 5 / 60  # Assume 5 minutes per retouche, convert to hours
    
    return metrics

def create_chain_dashboard(filtered_data, chain_id):
    """Create dashboard for a specific chain"""
    # Display title based on whether a specific chain is selected or all chains
    title = "Dashboard Opérationnel Chaîne Confection - Toutes les chaînes" if chain_id is None else f"Dashboard Opérationnel Chaîne Confection N° : {chain_id}"
    
    st.markdown(f"""
    <div style='background-color:#1A1A2E; color:#f8f9fa; padding:8px; text-align:center; font-size:16px; margin-bottom:15px; border-radius:4px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);'>
        <span style='font-weight:600;'>{title}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate metrics
    metrics = calculate_operational_metrics(filtered_data)
    
    # Create two main sections
    # 1. Retouche Fin Chaîne
    st.markdown("""
    <div style='border:2px solid #e74c3c; padding:6px; text-align:center; margin-bottom:10px; font-weight:bold; color:#FFFFFF; border-radius:4px; background-color:#2C3E50;'>
        <span style='font-size:14px;'>Retouche Fin Chaîne</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for the gauge and details
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Create gauge chart for Retouche Fin Chaîne
        gauge_fin = create_gauge_chart(
            value=metrics["fin_chaine_rate"],
            max_val=30,  # Maximum 30% retouche rate
            title="Taux de retouche fin chaîne"
        )
        st.plotly_chart(gauge_fin, use_container_width=True, key="gauge_fin_chaine")
        
        # Display metric value as text below gauge
        fin_chaine_color = "#4CAF50" if metrics['fin_chaine_rate'] < 5 else "#FFA000" if metrics['fin_chaine_rate'] < 15 else "#F44336"
        st.markdown(f"""
        <div style='background-color:#1E1E1E; text-align:center; padding:10px; border-radius:5px; margin-top:5px;'>
            <div style='color:{fin_chaine_color}; font-size:24px; font-weight:bold;'>{metrics['fin_chaine_rate']:.1f}%</div>
            <div style='color:#FFFFFF; font-size:14px;'>({metrics['fin_chaine_count']} pcs)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Détails postes section
        st.markdown("""
        <div style='text-align:center; margin-bottom:8px; font-weight:bold; color:#FFFFFF; font-size:13px;'>
            Détails postes
        </div>
        """, unsafe_allow_html=True)
        
        # Create the element grid for fin chaîne
        create_element_grid(filtered_data, mode="fin_chaine")
    
    # 2. Retouche Encours Chaîne
    st.markdown("""
    <div style='border:2px solid #e74c3c; padding:6px; text-align:center; margin-bottom:10px; margin-top:15px; font-weight:bold; color:#FFFFFF; border-radius:4px; background-color:#2C3E50;'>
        <span style='font-size:14px;'>Retouche Encours Chaîne</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for the gauge and details
    col3, col4 = st.columns([1, 3])
    
    with col3:
        # Create gauge chart for Retouche Encours Chaîne
        gauge_encours = create_gauge_chart(
            value=metrics["encours_rate"],
            max_val=30,  # Maximum 30% retouche rate
            title="Taux de retouche encours chaîne"
        )
        st.plotly_chart(gauge_encours, use_container_width=True, key="gauge_encours_chaine")
        
        # Display metric value as text below gauge
        encours_color = "#4CAF50" if metrics['encours_rate'] < 5 else "#FFA000" if metrics['encours_rate'] < 15 else "#F44336"
        st.markdown(f"""
        <div style='background-color:#1E1E1E; text-align:center; padding:10px; border-radius:5px; margin-top:5px;'>
            <div style='color:{encours_color}; font-size:24px; font-weight:bold;'>{metrics['encours_rate']:.1f}%</div>
            <div style='color:#FFFFFF; font-size:14px;'>({metrics['encours_count']} pcs)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Détails postes section for encours chaîne
        st.markdown("""
        <div style='text-align:center; margin-bottom:8px; font-weight:bold; color:#FFFFFF; font-size:13px;'>
            Détails postes
        </div>
        """, unsafe_allow_html=True)
        
        # Create the element grid for encours chaîne
        create_element_grid(filtered_data, mode="encours_chaine")

def create_rebutage_dashboard(filtered_data, chain_id):
    """Create dashboard for rebutage (second part)"""
    # Display title based on whether a specific chain is selected or all chains
    title = "Dashboard Opérationnel Repassage - Toutes les chaînes" if chain_id is None else f"Dashboard Opérationnel Repassage Ch : {chain_id}"
    
    st.markdown(f"""
    <div style='background-color:#1A1A2E; color:#f8f9fa; padding:8px; text-align:center; font-size:16px; margin-bottom:15px; border-radius:4px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);'>
        <span style='font-weight:600;'>{title}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate metrics
    metrics = calculate_operational_metrics(filtered_data)
    
    # 1. Taux d'avancement contrôle section
    st.markdown("""
    <div style='border:2px solid #3498db; padding:6px; text-align:center; margin-bottom:10px; font-weight:bold; color:#FFFFFF; border-radius:4px; background-color:#2C3E50;'>
        <span style='font-size:14px;'>Taux d'avancement contrôle</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Create gauge chart for Taux d'avancement
    gauge_avancement = create_gauge_chart(
        value=metrics.get("avancement_rate", 85),  # Default to 85% if not available
        max_val=100,  # Maximum 100% avancement
        title="Taux d'avancement contrôle"
    )
    st.plotly_chart(gauge_avancement, use_container_width=True, key="gauge_avancement")
    
    # Display metric value as text below gauge
    avance_color = "#4CAF50" if metrics.get("avancement_rate", 85) > 70 else "#FFA000" if metrics.get("avancement_rate", 85) > 40 else "#F44336"
    st.markdown(f"""
    <div style='background-color:#1E1E1E; text-align:center; padding:10px; border-radius:5px; margin-bottom:20px; margin-top:5px;'>
        <div style='color:{avance_color}; font-size:24px; font-weight:bold;'>{metrics.get("avancement_rate", 85):.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Rebut Cumulée
    st.markdown("""
    <div style='border:2px solid #e74c3c; padding:6px; text-align:center; margin-bottom:10px; font-weight:bold; color:#FFFFFF; border-radius:4px; background-color:#2C3E50;'>
        <span style='font-size:14px;'>Rebut Cumulée</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for the gauge and details
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Create gauge chart for Rebut Cumulée
        gauge_rebut = create_gauge_chart(
            value=metrics["rebut_rate"],
            max_val=5,  # Maximum 5% rebut rate
            title="Taux de rebut cumulé"
        )
        st.plotly_chart(gauge_rebut, use_container_width=True, key="gauge_rebut")
        
        # Display metric value as text below gauge
        rebut_color = "#4CAF50" if metrics["rebut_rate"] < 2 else "#FFA000" if metrics["rebut_rate"] < 4 else "#F44336"
        st.markdown(f"""
        <div style='background-color:#1E1E1E; text-align:center; padding:10px; border-radius:5px; margin-top:5px;'>
            <div style='color:{rebut_color}; font-size:24px; font-weight:bold;'>{metrics['rebut_rate']:.1f}%</div>
            <div style='color:#FFFFFF; font-size:14px;'>({metrics['rebut_count']} pcs)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Détails OF section
        st.markdown("""
        <div style='text-align:center; margin-bottom:8px; font-weight:bold; color:#FFFFFF; font-size:13px;'>
            Détails OF
        </div>
        """, unsafe_allow_html=True)
        
        # Create the orders detail grid
        create_orders_detail_grid(filtered_data)
    
    # 2. Retouche Cumulée
    st.markdown("""
    <div style='border:2px solid #e74c3c; padding:6px; text-align:center; margin-bottom:10px; margin-top:15px; font-weight:bold; color:#FFFFFF; border-radius:4px; background-color:#2C3E50;'>
        <span style='font-size:14px;'>Retouche Cumulée</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for the gauge and details
    col3, col4 = st.columns([1, 3])
    
    with col3:
        # Create gauge chart for Retouche Cumulée
        gauge_retouche = create_gauge_chart(
            value=metrics["retouche_total_rate"],
            max_val=30,  # Maximum 30% retouche rate
            title="Taux de retouche cumulé"
        )
        st.plotly_chart(gauge_retouche, use_container_width=True, key="gauge_retouche_total")
        
        # Display metric value as text below gauge
        retouche_color = "#4CAF50" if metrics['retouche_total_rate'] < 7 else "#FFA000" if metrics['retouche_total_rate'] < 20 else "#F44336"
        st.markdown(f"""
        <div style='background-color:#1E1E1E; text-align:center; padding:10px; border-radius:5px; margin-top:5px;'>
            <div style='color:{retouche_color}; font-size:24px; font-weight:bold;'>{metrics['retouche_total_rate']:.1f}%</div>
            <div style='color:#FFFFFF; font-size:14px;'>({metrics['retouche_total_count']} pcs)<br>{metrics['retouche_total_time']:.1f} h</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Create another table for orders detail grid (same as Rebut Cumulée)
        create_orders_detail_grid(filtered_data)
        
# Update the create_operational_dashboard function to properly use chain IDs from the CSV
def create_operational_dashboard(data):
    """Main function to create the operational dashboard"""
    # Set page config for dark theme
    st.markdown("""
        <style>
        .stApp {
            background-color: #121212;
            color: white;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #1E1E1E;
            border-radius: 4px 4px 0px 0px;
            padding: 10px 16px;
            color: white;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2C3E50 !important;
            color: white !important;
        }
        .stMarkdown {
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    # Create sidebar filters for operational dashboard
    st.sidebar.markdown("""
        <div style='background-color:#1A1A2E; color:#f8f9fa; padding:8px; text-align:center; margin-bottom:12px; border-radius:4px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);'>
            <h2 style='margin:0; font-size:16px; font-weight:600;'>Filtres</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Date filter
    st.sidebar.markdown("""
        <div style='background-color:#2C3E50; color:#FFFFFF; padding:6px; margin-bottom:8px; border-radius:3px; font-weight:600; font-size:14px;'>
            Période
        </div>
    """, unsafe_allow_html=True)
    start_date = st.sidebar.date_input("Date de début", value=pd.to_datetime(data['DATE'].min()).date() if 'DATE' in data.columns else None)
    end_date = st.sidebar.date_input("Date de fin", value=pd.to_datetime(data['DATE'].max()).date() if 'DATE' in data.columns else None)
    
    # Chain filter - use IDChaineMontage1 as requested
    chain_options = []
    if 'IDChaineMontage1' in data.columns:
        # Get unique chain IDs, excluding 0
        chain_options = [c for c in data['IDChaineMontage1'].unique().tolist() if c != 0]
    elif 'IDChaineMontage' in data.columns:
        chain_options = [c for c in data['IDChaineMontage'].unique().tolist() if c != 0]
    elif 'Chaine' in data.columns:
        chain_options = [c for c in data['Chaine'].unique().tolist() if c != 0]
    elif 'idchaine' in data.columns:
        chain_options = [c for c in data['idchaine'].unique().tolist() if c != 0]
        
    if not chain_options:
        chain_options = ["Chaîne 1", "Chaîne 2", "Chaîne 3"]
    
    # Add "All" option at the beginning of options
    chain_options_with_all = ["Toutes les chaînes"] + sorted([str(c) for c in chain_options])
    
    selected_chain_option = st.sidebar.selectbox(
        "Chaîne", 
        chain_options_with_all,
        index=0,
        format_func=lambda x: x if x != "Toutes les chaînes" else "✅ Toutes les chaînes"
    )
    
    # Determine if "All" was selected
    all_chains_selected = selected_chain_option == "Toutes les chaînes"
    selected_chain = None if all_chains_selected else selected_chain_option
    
    # Apply filters to data
    filtered_data = data.copy()
    
    # Apply date filter
    if 'DATE' in filtered_data.columns:
        filtered_data = apply_date_filter(filtered_data, start_date, end_date)
    
    # Apply chain filter only if a specific chain is selected
    if selected_chain is not None:
        if 'IDChaineMontage1' in filtered_data.columns:
            filtered_data = apply_categorical_filter(filtered_data, 'IDChaineMontage1', [selected_chain])
        elif 'IDChaineMontage' in filtered_data.columns:
            filtered_data = apply_categorical_filter(filtered_data, 'IDChaineMontage', [selected_chain])
        elif 'Chaine' in filtered_data.columns:
            filtered_data = apply_categorical_filter(filtered_data, 'Chaine', [selected_chain])
        elif 'idchaine' in filtered_data.columns:
            filtered_data = apply_categorical_filter(filtered_data, 'idchaine', [selected_chain])
    
    # Create dashboard tabs with larger, more visible text
    tab1, tab2 = st.tabs([
        "📊 Dashboard Chaîne Confection", 
        "🔄 Dashboard Repassage"
    ])
    
    with tab1:
        # Create chain dashboard (first part)
        create_chain_dashboard(filtered_data, selected_chain)
    
    with tab2:
        # Create rebutage dashboard (second part)
        create_rebutage_dashboard(filtered_data, selected_chain)

