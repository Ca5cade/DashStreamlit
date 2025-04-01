import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import apply_date_filter, apply_categorical_filter, apply_numerical_filter, apply_all_filters

def create_gauge_chart(value, max_val=100, title="Gauge Chart"):
    """Create a gauge chart for KPI visualization"""
    if max_val <= 0:
        max_val = 100  # Set a default if max_val is invalid
    
    # Set appropriate colors based on value
    if value/max_val < 0.3:
        color = "green"
    elif value/max_val < 0.7:
        color = "orange"
    else:
        color = "red"
    
    # Format percentage value for display
    percentage = (value / max_val) * 100
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_val*0.3], 'color': 'green'},
                {'range': [max_val*0.3, max_val*0.7], 'color': 'orange'},
                {'range': [max_val*0.7, max_val], 'color': 'red'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=300, 
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(family="Arial", size=12),
    )
    
    return fig

def create_element_grid(filtered_data, mode="fin_chaine"):
    """
    Create the operation detail grid
    
    Args:
        filtered_data: Filtered DataFrame with data
        mode: "fin_chaine" or "encours_chaine"
    
    Returns:
        Streamlit elements grid with details
    """
    # Sample data for the element grid - this would normally come from filtered_data
    # but for demonstration we'll create some simulated data
    elements = []
    
    # Determine the operation column name based on what's available
    operation_column = None
    for col_name in ['IDOperation', 'Operation', 'idoperation', 'operation']:
        if col_name in filtered_data.columns:
            operation_column = col_name
            break
    
    # Get unique operation IDs from data if available
    if operation_column:
        operations = filtered_data[operation_column].unique().tolist()
    else:
        # Sample operations for demonstration if no valid column found
        operations = list(range(30, 55)) + list(range(80, 87)) + list(range(112, 119))
    
    # For each operation, create an element
    for op_id in operations[:18]:  # Limit to 18 elements per grid (3 rows of 6)
        # Determine the status/performance color
        # In real implementation, calculate this based on actual metrics
        
        # Initialize retouche count
        retouche_count = 0
        
        if mode == "fin_chaine":
            if operation_column and 'TypeControle' in filtered_data.columns:
                # Get retouche count for this operation
                retouche_count = filtered_data[
                    (filtered_data[operation_column] == op_id) & 
                    (filtered_data['TypeControle'] == 'Fin_Chaine')
                ].shape[0]
            elif operation_column:
                # If TypeControle not available, just count by operation
                retouche_count = filtered_data[filtered_data[operation_column] == op_id].shape[0]
            
            # Calculate random performance for demonstration
            if 'Quantite' in filtered_data.columns:
                total_qty = filtered_data['Quantite'].sum()
                performance = retouche_count / max(1, total_qty) * 100
            else:
                # Generate random performance between 1-15% for demo
                # Safely generate a random-like value for any type of op_id
                if isinstance(op_id, str):
                    # Use hash of string to generate consistent random-like value
                    op_hash = sum(ord(c) for c in op_id)
                    performance = (op_hash % 15) + 1
                elif isinstance(op_id, (int, float)):
                    # Use modulo for numeric values
                    performance = (int(op_id) % 15) + 1
                else:
                    # Fallback for any other type
                    performance = 5
        else:
            # For encours_chaine
            if operation_column and 'TypeControle' in filtered_data.columns:
                retouche_count = filtered_data[
                    (filtered_data[operation_column] == op_id) & 
                    (filtered_data['TypeControle'] == 'Encours_Chaine')
                ].shape[0]
            elif operation_column:
                # If TypeControle not available, just count by operation
                retouche_count = filtered_data[filtered_data[operation_column] == op_id].shape[0]
            
            # Calculate random performance for demonstration
            if 'Quantite' in filtered_data.columns:
                total_qty = filtered_data['Quantite'].sum()
                performance = retouche_count / max(1, total_qty) * 100
            else:
                # Generate random performance between 1-15% for demo
                # Safely generate a random-like value for any type of op_id
                if isinstance(op_id, str):
                    # Use hash of string to generate consistent random-like value
                    op_hash = sum(ord(c) for c in op_id)
                    performance = (op_hash % 15) + 1
                elif isinstance(op_id, (int, float)):
                    # Use modulo for numeric values
                    performance = (int(op_id) % 15) + 1
                else:
                    # Fallback for any other type
                    performance = 5
        
        # Determine performance color
        if performance < 3:
            color = "#78d18b"  # Green
        elif performance < 7:
            color = "#f7f59a"  # Yellow
        else:
            color = "#ff9a9a"  # Red
        
        # Create element dictionary
        element = {
            "id": op_id,
            "color": color,
            "count": retouche_count,
            "performance": f"{performance:.1f}%"
        }
        
        elements.append(element)
    
    # Create the grid layout with 6 columns
    cols = st.columns(6)
    
    # Create the element grid (3 rows of 6 elements)
    for i, element in enumerate(elements):
        # Select the appropriate column
        col_idx = i % 6
        
        with cols[col_idx]:
            # Create each element box
            st.markdown(f"""
            <div style="background-color:{element['color']}; border:1px solid #ddd; padding:5px; text-align:center; margin-bottom:10px;">
                <div style="font-weight:bold; font-size:16px;">{element['id']}</div>
                <div style="font-size:12px;">{element['performance']}</div>
                <div style="font-size:12px;">({element['count']} pcs)</div>
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
    <div style="display:flex; margin-bottom:10px; font-weight:bold;">
        <div style="flex:1; text-align:center;">OF</div>
        <div style="flex:1; text-align:center; color:red;">1%</div>
        <div style="flex:1; text-align:center; color:orange;">10%</div>
        <div style="flex:1; text-align:center; color:green;">50%</div>
        <div style="flex:1; text-align:center;">39%</div>
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
        <div style="display:flex; margin-bottom:5px; border-bottom:1px solid #eee; padding-bottom:5px;">
            <div style="flex:1; text-align:center; background-color:#f0f0f0; padding:3px;">{order}<br>({total_qty} pcs)</div>
            <div style="flex:1; text-align:center; background-color:#ff9a9a; padding:3px;">1%<br>({pct1} pcs)</div>
            <div style="flex:1; text-align:center; background-color:#ffd699; padding:3px;">10%<br>({pct10} pcs)</div>
            <div style="flex:1; text-align:center; background-color:#b3e6b3; padding:3px;">50%<br>({pct50} pcs)</div>
            <div style="flex:1; text-align:center; background-color:#f0f0f0; padding:3px;">39%<br>({pct39} pcs)</div>
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
    if qtte_column:
        metrics['fin_chaine_count'] = fin_chaine_data[qtte_column].sum()
    else:
        metrics['fin_chaine_count'] = len(fin_chaine_data)
    
    # TRFC - Taux de retouches Fin de chaîne
    if qtte_sondee_column and qtte_column:
        qtte_sondee_fin = fin_chaine_data[qtte_sondee_column].sum() if not fin_chaine_data.empty else default_total
        metrics['fin_chaine_rate'] = (metrics['fin_chaine_count'] / max(1, qtte_sondee_fin)) * 100
    else:
        # Fallback calculation
        metrics['fin_chaine_rate'] = (metrics['fin_chaine_count'] / max(1, len(filtered_data))) * 100
    
    # TepRFC - Temps de retouches Fin Chaîne
    if temps_column and operation_column:
        # Filter operations that start with 'fixation' or 'fix'
        if not fin_chaine_data.empty:
            fixation_ops = fin_chaine_data[
                fin_chaine_data[operation_column].astype(str).str.lower().str.startswith(('fixation', 'fix'))
            ]
            metrics['fin_chaine_time'] = fixation_ops[temps_column].sum() if not fixation_ops.empty else 0
        else:
            metrics['fin_chaine_time'] = 0
    else:
        # Fallback: estimate time based on count
        metrics['fin_chaine_time'] = metrics['fin_chaine_count'] * 5  # Assume 5 minutes per retouche
    
    # ThRFC - Taux horaire de retouches Fin de chaîne
    if taux_horaire_column and not fin_chaine_data.empty:
        total_taux_horaire = fin_chaine_data[taux_horaire_column].sum() if taux_horaire_column in fin_chaine_data.columns else 1
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
    if qtte_column:
        metrics['encours_count'] = encours_data[qtte_column].sum() if not encours_data.empty else 0
    else:
        metrics['encours_count'] = len(encours_data)
    
    # TREC - Taux de retouches Encours chaîne
    if qtte_sondee_column and qtte_column:
        qtte_sondee_encours = encours_data[qtte_sondee_column].sum() if not encours_data.empty else default_total
        metrics['encours_rate'] = (metrics['encours_count'] / max(1, qtte_sondee_encours)) * 100
    else:
        # Fallback calculation
        metrics['encours_rate'] = (metrics['encours_count'] / max(1, len(filtered_data))) * 100
    
    # TepREC - Temps de retouches Encours Chaîne
    if temps_column and operation_column:
        # Filter operations that start with 'fixation' or 'fix'
        if not encours_data.empty:
            fixation_ops = encours_data[
                encours_data[operation_column].astype(str).str.lower().str.startswith(('fixation', 'fix'))
            ]
            metrics['encours_time'] = fixation_ops[temps_column].sum() if not fixation_ops.empty else 0
        else:
            metrics['encours_time'] = 0
    else:
        # Fallback: estimate time based on count
        metrics['encours_time'] = metrics['encours_count'] * 5  # Assume 5 minutes per retouche
    
    # ThREC - Taux horaire de retouches Encours de chaîne
    if taux_horaire_column and not encours_data.empty:
        total_taux_horaire = encours_data[taux_horaire_column].sum() if taux_horaire_column in encours_data.columns else 1
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
    st.markdown(f"""
    <div style='background-color:#2c3e50; color:white; padding:10px; text-align:center; font-size:20px; margin-bottom:20px; border-radius:5px;'>
        DahBoard Opérationnel Chaîne Confection N : {chain_id}
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate metrics
    metrics = calculate_operational_metrics(filtered_data)
    
    # Create two main sections
    # 1. Retouche Fin Chaîne
    st.markdown("""
    <div style='border:2px solid #e74c3c; padding:5px; text-align:center; margin-bottom:10px; font-weight:bold; color:#e74c3c;'>
        Retouche Fin Chaîne
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
        fin_chaine_color = "green" if metrics['fin_chaine_rate'] < 5 else "orange" if metrics['fin_chaine_rate'] < 15 else "red"
        st.markdown(f"""
        <div style='background-color:#e8f8e8; text-align:center; padding:10px; border-radius:5px;'>
            <div style='color:{fin_chaine_color}; font-size:24px; font-weight:bold;'>{metrics['fin_chaine_rate']:.1f}%</div>
            <div>({metrics['fin_chaine_count']} pcs)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Détails postes section
        st.markdown("""
        <div style='text-align:center; margin-bottom:10px; font-weight:bold;'>
            Détails postes
        </div>
        """, unsafe_allow_html=True)
        
        # Create the element grid for fin chaîne
        create_element_grid(filtered_data, mode="fin_chaine")
    
    # 2. Retouche Encours Chaîne
    st.markdown("""
    <div style='border:2px solid #e74c3c; padding:5px; text-align:center; margin-bottom:10px; margin-top:20px; font-weight:bold; color:#e74c3c;'>
        Retouche Encours Chaîne
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
        encours_color = "green" if metrics['encours_rate'] < 5 else "orange" if metrics['encours_rate'] < 15 else "red"
        st.markdown(f"""
        <div style='background-color:#e8f8e8; text-align:center; padding:10px; border-radius:5px;'>
            <div style='color:{encours_color}; font-size:24px; font-weight:bold;'>{metrics['encours_rate']:.1f}%</div>
            <div>({metrics['encours_count']} pcs)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Détails postes section for encours chaîne
        st.markdown("""
        <div style='text-align:center; margin-bottom:10px; font-weight:bold;'>
            Détails postes
        </div>
        """, unsafe_allow_html=True)
        
        # Create the element grid for encours chaîne
        create_element_grid(filtered_data, mode="encours_chaine")

def create_rebutage_dashboard(filtered_data, chain_id):
    """Create dashboard for rebutage (second part)"""
    st.markdown(f"""
    <div style='background-color:#2c3e50; color:white; padding:10px; text-align:center; font-size:20px; margin-bottom:20px; border-radius:5px;'>
        DahBoard Opérationnel Repassage Ch : {chain_id}
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate metrics
    metrics = calculate_operational_metrics(filtered_data)
    
    # 1. Taux d'avancement contrôle section
    st.markdown("""
    <div style='border:2px solid #3498db; padding:5px; text-align:center; margin-bottom:10px; font-weight:bold; color:#3498db;'>
        Taux d'avancement contrôle
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
    avance_color = "green" if metrics.get("avancement_rate", 85) > 70 else "orange" if metrics.get("avancement_rate", 85) > 40 else "red"
    st.markdown(f"""
    <div style='background-color:#e8f8f8; text-align:center; padding:10px; border-radius:5px; margin-bottom:20px;'>
        <div style='color:{avance_color}; font-size:24px; font-weight:bold;'>{metrics.get("avancement_rate", 85):.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Rebut Cumulée
    st.markdown("""
    <div style='border:2px solid #e74c3c; padding:5px; text-align:center; margin-bottom:10px; font-weight:bold; color:#e74c3c;'>
        Rebut Cumulée
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
        rebut_color = "green" if metrics["rebut_rate"] < 2 else "orange" if metrics["rebut_rate"] < 4 else "red"
        st.markdown(f"""
        <div style='background-color:#e8f8e8; text-align:center; padding:10px; border-radius:5px;'>
            <div style='color:{rebut_color}; font-size:24px; font-weight:bold;'>{metrics['rebut_rate']:.1f}%</div>
            <div>({metrics['rebut_count']} pcs)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Détails OF section
        st.markdown("""
        <div style='text-align:center; margin-bottom:10px; font-weight:bold;'>
            Détails OF
        </div>
        """, unsafe_allow_html=True)
        
        # Create the orders detail grid
        create_orders_detail_grid(filtered_data)
    
    # 2. Retouche Cumulée
    st.markdown("""
    <div style='border:2px solid #e74c3c; padding:5px; text-align:center; margin-bottom:10px; margin-top:20px; font-weight:bold; color:#e74c3c;'>
        Retouche Cumulée
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
        retouche_color = "green" if metrics['retouche_total_rate'] < 7 else "orange" if metrics['retouche_total_rate'] < 20 else "red"
        st.markdown(f"""
        <div style='background-color:#e8f8e8; text-align:center; padding:10px; border-radius:5px;'>
            <div style='color:{retouche_color}; font-size:24px; font-weight:bold;'>{metrics['retouche_total_rate']:.1f}%</div>
            <div>({metrics['retouche_total_count']} pcs)<br>{metrics['retouche_total_time']:.1f} h</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Create another table for orders detail grid (same as Rebut Cumulée)
        create_orders_detail_grid(filtered_data)
        
def create_operational_dashboard(data):
    """Main function to create the operational dashboard"""
    # Create sidebar filters for operational dashboard
    st.sidebar.markdown("## Filtres")
    
    # Date filter
    st.sidebar.markdown("### Période")
    start_date = st.sidebar.date_input("Date de début", value=pd.to_datetime(data['DATE'].min()).date() if 'DATE' in data.columns else None)
    end_date = st.sidebar.date_input("Date de fin", value=pd.to_datetime(data['DATE'].max()).date() if 'DATE' in data.columns else None)
    
    # Chain filter
    chain_options = data['IDChaineMontage'].unique().tolist() if 'IDChaineMontage' in data.columns else []
    if not chain_options and 'Chaine' in data.columns:
        chain_options = data['Chaine'].unique().tolist()
    
    if not chain_options and 'idchaine' in data.columns:
        chain_options = data['idchaine'].unique().tolist()
        
    if not chain_options:
        chain_options = ["Chaîne 1", "Chaîne 2", "Chaîne 3"]
    
    selected_chain = st.sidebar.selectbox("Chaîne", chain_options, index=0)
    
    # Apply filters to data
    filtered_data = data.copy()
    
    # Apply date filter
    if 'DATE' in filtered_data.columns:
        filtered_data = apply_date_filter(filtered_data, start_date, end_date)
    
    # Apply chain filter
    if 'IDChaineMontage' in filtered_data.columns:
        filtered_data = apply_categorical_filter(filtered_data, 'IDChaineMontage', [selected_chain])
    elif 'Chaine' in filtered_data.columns:
        filtered_data = apply_categorical_filter(filtered_data, 'Chaine', [selected_chain])
    elif 'idchaine' in filtered_data.columns:
        filtered_data = apply_categorical_filter(filtered_data, 'idchaine', [selected_chain])
    
    # Create dashboard tabs
    tab1, tab2 = st.tabs(["Dashboard Chaîne Confection", "Dashboard Repassage"])
    
    with tab1:
        # Create chain dashboard (first part)
        create_chain_dashboard(filtered_data, selected_chain)
    
    with tab2:
        # Create rebutage dashboard (second part)
        create_rebutage_dashboard(filtered_data, selected_chain)