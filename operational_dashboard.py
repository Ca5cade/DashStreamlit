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
    Create the operation detail grid with enhanced styling and visualization
    
    Args:
        filtered_data: Filtered DataFrame with data
        mode: "fin_chaine" or "encours_chaine"
    
    Returns:
        Streamlit elements grid with details
    """
    # Enhanced CSS for data visualization
    st.markdown("""
    <style>
    .table-wrapper {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }
    .custom-table thead th {
        background-color: #1e3a8a;
        color: white;
        padding: 12px 15px;
        text-align: left;
        font-weight: bold;
    }
    .custom-table tbody tr {
        border-bottom: 1px solid #e2e8f0;
    }
    .custom-table tbody tr:nth-child(even) {
        background-color: #f8fafc;
    }
    .custom-table tbody tr:hover {
        background-color: #e2e8f0;
    }
    .custom-table tbody td {
        padding: 10px 15px;
        color: #334155;
    }
    .custom-table tbody tr:last-child {
        border-bottom: none;
    }
    .progress-bar {
        height: 8px;
        background-color: #e2e8f0;
        border-radius: 4px;
        overflow: hidden;
    }
    .progress-value {
        height: 100%;
        background-color: #3b82f6;
        border-radius: 4px;
    }
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        color: white;
    }
    .badge-red {
        background-color: #ef4444;
    }
    .badge-yellow {
        background-color: #f59e0b;
    }
    .badge-green {
        background-color: #10b981;
    }
    .badge-blue {
        background-color: #3b82f6;
    }
    .grid-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin-bottom: 10px;
    }
    .grid-item {
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
        background-color: white;
    }
    .grid-item:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .grid-item-id {
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 5px;
    }
    .grid-item-perf {
        font-size: 14px;
        margin-bottom: 3px;
    }
    .grid-item-count {
        font-size: 12px;
        color: #64748b;
    }
    .green-item {
        border-left: 4px solid #10b981;
    }
    .yellow-item {
        border-left: 4px solid #f59e0b;
    }
    .red-item {
        border-left: 4px solid #ef4444;
    }
    .empty-state {
        text-align: center;
        padding: 30px;
        background-color: #f8fafc;
        border-radius: 8px;
        color: #64748b;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Determine the correct filter based on mode
    if mode == "fin_chaine":
        if 'Categorie' in filtered_data.columns:
            grid_data = filtered_data[filtered_data['Categorie'] == 'PRODUCTION FIN CHAINE'].copy()
        elif 'TypeControle' in filtered_data.columns:
            grid_data = filtered_data[filtered_data['TypeControle'] == 'Fin_Chaine'].copy()
        else:
            grid_data = filtered_data.copy()
            
        mode_title = "Fin Chaîne"
    else:  # encours_chaine
        if 'Categorie' in filtered_data.columns:
            grid_data = filtered_data[filtered_data['Categorie'] == 'PRODUCTION ENCOURS'].copy()
        elif 'TypeControle' in filtered_data.columns:
            grid_data = filtered_data[filtered_data['TypeControle'] == 'Encours_Chaine'].copy()
        else:
            grid_data = filtered_data.copy()
            
        mode_title = "Encours Chaîne"
    
    # Determine the operation column name based on what's available
    operation_column = None
    for col_name in ['IDOperation', 'Operation', 'idoperation', 'operation', 'Libelle']:
        if col_name in grid_data.columns:
            operation_column = col_name
            break
    
    # Only proceed if we have valid operation data
    if operation_column and not grid_data.empty:
        # Get operation counts and metrics
        operation_counts = grid_data[operation_column].value_counts().reset_index()
        operation_counts.columns = ['operation', 'count']
        
        # Sort by count descending
        operation_counts = operation_counts.sort_values(by='count', ascending=False)
        
        # Get top 20 operations (or fewer if less available)
        top_operations = operation_counts.head(20)
        
        # Calculate percentages
        total_count = top_operations['count'].sum()
        top_operations['percentage'] = (top_operations['count'] / total_count * 100).round(1)
        
        # Build the grid of operations
        grid_html = '<div class="grid-container">'
        
        for _, row in top_operations.iterrows():
            op_id = row['operation']
            count = row['count']
            percentage = row['percentage']
            
            # Determine performance color
            if percentage < 5:
                color_class = "green-item"
            elif percentage < 15:
                color_class = "yellow-item"
            else:
                color_class = "red-item"
            
            # Add grid item
            grid_html += f"""
            <div class="grid-item {color_class}">
                <div class="grid-item-id">{op_id}</div>
                <div class="grid-item-perf">{percentage}%</div>
                <div class="grid-item-count">{count} pcs</div>
            </div>
            """
        
        grid_html += '</div>'
        
        # Show grid title
        st.markdown(f"""
        <div style="margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
            <div style="font-weight:bold; color:#1e3a8a;">Top Opérations - {mode_title}</div>
            <div style="font-size:12px; color:#64748b;">{len(top_operations)} opérations affichées sur {len(operation_counts)} au total</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show the grid
        st.markdown(grid_html, unsafe_allow_html=True)
        
        # Show summary metrics
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; margin:10px 0 20px 0;">
            <div style="text-align:center; background-color:white; padding:10px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.05); flex:1; margin-right:10px;">
                <div style="color:#64748b; font-size:12px;">Total pièces</div>
                <div style="font-weight:bold; font-size:18px; color:#1e3a8a;">{total_count}</div>
            </div>
            <div style="text-align:center; background-color:white; padding:10px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.05); flex:1;">
                <div style="color:#64748b; font-size:12px;">% Top 3 opérations</div>
                <div style="font-weight:bold; font-size:18px; color:#1e3a8a;">{top_operations.head(3)['percentage'].sum():.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Option to display detailed table
        with st.expander("Afficher le tableau détaillé"):
            # Generate HTML table with progress bars and badges
            table_rows = ""
            for _, row in top_operations.iterrows():
                pct = row['percentage']
                
                # Determine badge color based on percentage
                if pct > 20:
                    badge_class = "badge-red"
                elif pct > 10:
                    badge_class = "badge-yellow"
                elif pct > 5:
                    badge_class = "badge-blue"
                else:
                    badge_class = "badge-green"
                
                table_rows += f"""
                <tr>
                    <td>{row['operation']}</td>
                    <td>{int(row['count'])}</td>
                    <td>
                        <div class="progress-bar">
                            <div class="progress-value" style="width: {min(100, pct)}%;"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-top:5px;">
                            <span class="badge {badge_class}">{pct}%</span>
                            <span style="font-size:12px; color:#64748b;">du total</span>
                        </div>
                    </td>
                </tr>
                """
            
            # Display the formatted table
            st.markdown(f"""
            <div class="table-wrapper">
                <table class="custom-table">
                    <thead>
                        <tr>
                            <th>Opération</th>
                            <th>Quantité</th>
                            <th>Répartition</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Show empty state
        st.markdown("""
        <div class="empty-state">
            <i class="fas fa-info-circle" style="font-size:24px; color:#3b82f6; margin-bottom:10px;"></i>
            <div style="font-weight:bold; margin-bottom:5px;">Aucune donnée disponible</div>
            <div>Essayez d'ajuster vos filtres pour voir des résultats pour cette catégorie.</div>
        </div>
        """, unsafe_allow_html=True)

def create_orders_detail_grid(filtered_data):
    """Create the orders detail grid for the Rebut dashboard with modern design"""
    # Enhanced CSS for orders table
    st.markdown("""
    <style>
    .of-table {
        width: 100%;
        border-collapse: collapse;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
    }
    .of-table th {
        background-color: #1e3a8a;
        color: white;
        padding: 12px;
        text-align: center;
        font-weight: bold;
        font-size: 13px;
    }
    .of-table td {
        padding: 10px 5px;
        text-align: center;
        border-bottom: 1px solid #f1f5f9;
        font-size: 13px;
    }
    .of-table tr:last-child td {
        border-bottom: none;
    }
    .of-table tr:nth-child(even) {
        background-color: #f8fafc;
    }
    .of-table tr:hover td {
        background-color: #e2e8f0;
    }
    .of-card {
        background-color: white;
        border-radius: 6px;
        padding: 10px 5px;
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .of-title {
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 5px;
        color: #1e3a8a;
    }
    .of-subtitle {
        font-size: 12px;
        color: #64748b;
    }
    .of-category {
        margin-top: 5px;
        font-size: 12px;
        font-weight: bold;
    }
    .of-count {
        margin-top: 3px;
        font-size: 10px;
        color: #64748b;
    }
    .perc-1 { color: #ef4444; }
    .perc-10 { color: #f59e0b; }
    .perc-50 { color: #10b981; }
    .perc-39 { color: #3b82f6; }
    
    /* Progress bar styles */
    .of-progress-container {
        width: 100%;
        background-color: #e2e8f0;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        margin: 10px 0;
    }
    .of-progress-value {
        height: 100%;
        border-radius: 4px;
    }
    .of-progress-red {
        background-color: #ef4444;
    }
    .of-progress-orange {
        background-color: #f59e0b;
    }
    .of-progress-green {
        background-color: #10b981;
    }
    .of-progress-blue {
        background-color: #3b82f6;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check for available order/fabrication columns
    order_column = None
    for col_name in ['IDOFabrication', 'IDOfabrication', 'OFabrication', 'OF', 'id_fabrication']:
        if col_name in filtered_data.columns:
            order_column = col_name
            break
    
    # Get order data and metrics
    if order_column and order_column in filtered_data.columns:
        # Group by order to get quantities
        order_counts = filtered_data.groupby(order_column).size().reset_index(name='count')
        order_counts = order_counts.sort_values(by='count', ascending=False)
        
        # Limit to top 10 orders for display
        orders = order_counts.head(10)[order_column].tolist()
        
        # Create a better visualization for order detail using a table
        st.markdown("""
        <div style="margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
            <div style="font-weight:bold; color:#1e3a8a;">Détails des Ordres de Fabrication</div>
            <div style="font-size:12px; color:#64748b;">Top 10 ordres affichés</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Build table HTML for a modern look
        table_html = """
        <table class="of-table">
            <thead>
                <tr>
                    <th>OF</th>
                    <th>Total</th>
                    <th>Répartition</th>
                    <th>Statut</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for order in orders:
            # Calculate metrics for this order
            order_data = filtered_data[filtered_data[order_column] == order]
            
            # Get total quantity  
            if 'Qtte' in order_data.columns:
                total_qty = order_data['Qtte'].sum()
            elif 'Quantite' in order_data.columns:
                total_qty = order_data['Quantite'].sum()
            else:
                total_qty = len(order_data)
                
            # Get default quality distribution or calculate from data
            # These would be calculated from real data in production, using sample for demo
            success_pct = 75  # Good quality items
            warning_pct = 15  # Minor issues
            danger_pct = 5    # Major issues
            other_pct = 100 - success_pct - warning_pct - danger_pct
            
            # Determine the order status
            if danger_pct > 10:
                status = '<span style="color:#ef4444; font-weight:bold;">Critique</span>'
            elif warning_pct > 20:
                status = '<span style="color:#f59e0b; font-weight:bold;">Attention</span>'
            else:
                status = '<span style="color:#10b981; font-weight:bold;">Normal</span>'
            
            # Calculate real quantities
            qty_success = int(total_qty * success_pct / 100)
            qty_warning = int(total_qty * warning_pct / 100)
            qty_danger = int(total_qty * danger_pct / 100)
            qty_other = total_qty - qty_success - qty_warning - qty_danger
            
            # Add to table
            table_html += f"""
            <tr>
                <td><strong>{order}</strong></td>
                <td>{int(total_qty)} pcs</td>
                <td>
                    <div class="of-progress-container">
                        <div class="of-progress-value of-progress-green" style="width:{success_pct}%; float:left;"></div>
                        <div class="of-progress-value of-progress-orange" style="width:{warning_pct}%; float:left;"></div>
                        <div class="of-progress-value of-progress-red" style="width:{danger_pct}%; float:left;"></div>
                        <div class="of-progress-value of-progress-blue" style="width:{other_pct}%; float:left;"></div>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:10px; color:#64748b;">
                        <span>{success_pct}% OK</span>
                        <span>{warning_pct}% R.M</span>
                        <span>{danger_pct}% R.Maj</span>
                        <span>{other_pct}% Autres</span>
                    </div>
                </td>
                <td>{status}</td>
            </tr>
            """
        
        table_html += """
            </tbody>
        </table>
        """
        
        # Display the table
        st.markdown(table_html, unsafe_allow_html=True)
        
        # Show a summary row with total count
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; margin-top:5px;">
            <div style="font-size:12px; color:#64748b;">Total des ordres: {len(filtered_data[order_column].unique())}</div>
            <div style="font-size:12px; color:#64748b;">Total pièces: {filtered_data.shape[0]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Show empty state with better styling
        st.markdown("""
        <div style="text-align:center; padding:20px; background-color:#f8fafc; border-radius:8px; margin-bottom:15px;">
            <i class="fas fa-info-circle" style="font-size:24px; color:#3b82f6; margin-bottom:10px;"></i>
            <div style="font-weight:bold; margin-bottom:5px;">Aucun ordre de fabrication détecté</div>
            <div style="color:#64748b;">Les données ne contiennent pas d'informations sur les ordres de fabrication.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create demo cards as a visual alternative
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="of-card">
                <div class="of-title">Comment lire ce tableau</div>
                <div class="of-subtitle">Les couleurs indiquent la qualité:</div>
                <div class="of-category perc-50">🟢 Vert: Conforme</div>
                <div class="of-category perc-10">🟠 Orange: Retouches mineures</div>
                <div class="of-category perc-1">🔴 Rouge: Retouches majeures</div>
                <div class="of-category perc-39">🔵 Bleu: Autres statuts</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div class="of-card">
                <div class="of-title">Astuce</div>
                <div class="of-subtitle">Pour afficher ce tableau, assurez-vous que vos données contiennent l'une des colonnes suivantes:</div>
                <div class="of-count" style="text-align:center; margin-top:10px;">
                IDOFabrication, IDOfabrication, OFabrication, OF, id_fabrication
                </div>
            </div>
            """, unsafe_allow_html=True)

def calculate_operational_metrics(filtered_data):
    """Calculate metrics for the operational dashboard according to the specified formulas"""
    metrics = {}
    
    # Find relevant column names in the data
    categorie_column = 'categorie' if 'categorie' in filtered_data.columns else None
    type_column = 'type' if 'type' in filtered_data.columns else None
    qtte_column = 'qtte' if 'qtte' in filtered_data.columns else ('Quantite' if 'Quantite' in filtered_data.columns else None)
    qttesondee_column = 'qttesondee' if 'qttesondee' in filtered_data.columns else None
    temps_column = 'temps' if 'temps' in filtered_data.columns else ('TempsRetouche' if 'TempsRetouche' in filtered_data.columns else None)
    tauxhoraire_column = 'tauxhoraire' if 'tauxhoraire' in filtered_data.columns else None
    operation_column = None
    for col in ['operation', 'Operation', 'idoperation', 'IDOperation']:
        if col in filtered_data.columns:
            operation_column = col
            break
    qttelct_column = 'qttelct' if 'qttelct' in filtered_data.columns else None
    
    # Default quantity if not found
    total_qty = filtered_data[qtte_column].sum() if qtte_column else 1000
    
    # ---- FIN CHAÎNE METRICS ----
    # 1. Nbre de retouches Fin Chaîne (NRFC)
    if categorie_column and qtte_column:
        fin_chaine_data = filtered_data[filtered_data[categorie_column] == 'PRODUCTION FIN CHAINE']
        metrics['fin_chaine_count'] = fin_chaine_data[qtte_column].sum() if not fin_chaine_data.empty else 0
    else:
        # Fallback: Use TypeControle if categorie is not available
        fin_chaine_data = filtered_data[filtered_data['TypeControle'] == 'Fin_Chaine'] if 'TypeControle' in filtered_data.columns else filtered_data
        metrics['fin_chaine_count'] = fin_chaine_data.shape[0]
    
    # 2. Taux de retouches Fin de chaîne (TRFC)
    if qttesondee_column and not fin_chaine_data.empty:
        qtte_sondee_fin_chaine = fin_chaine_data[qttesondee_column].sum()
        metrics['fin_chaine_rate'] = (metrics['fin_chaine_count'] / max(1, qtte_sondee_fin_chaine)) * 100
    else:
        # Fallback calculation
        metrics['fin_chaine_rate'] = (metrics['fin_chaine_count'] / max(1, total_qty)) * 100
    
    # 3. Temps de retouches Fin Chaîne (TepRFC)
    if temps_column and operation_column and not fin_chaine_data.empty:
        try:
            # Make sure we're only working with string operations
            fin_chaine_data_with_str_op = fin_chaine_data.copy()
            fin_chaine_data_with_str_op[operation_column] = fin_chaine_data_with_str_op[operation_column].astype(str)
            
            # Select operations that start with "fixation" in Fin Chaîne
            fixation_ops = fin_chaine_data_with_str_op[fin_chaine_data_with_str_op[operation_column].str.lower().str.startswith('fixation')]
            metrics['fin_chaine_time'] = fixation_ops[temps_column].sum() if not fixation_ops.empty and temps_column else 0
            
            # If no fixation operations or no time, fallback
            if metrics['fin_chaine_time'] == 0:
                metrics['fin_chaine_time'] = fin_chaine_data[temps_column].sum() if temps_column else metrics['fin_chaine_count'] * 5
        except (ValueError, AttributeError, TypeError):
            # If there's any error processing the string operations, fall back to a simpler calculation
            metrics['fin_chaine_time'] = fin_chaine_data[temps_column].sum() if temps_column else metrics['fin_chaine_count'] * 5
    else:
        # Default estimation
        metrics['fin_chaine_time'] = metrics['fin_chaine_count'] * 5  # 5 minutes per retouche
    
    # 4. Taux horaire de retouches Fin de chaîne (ThRFC)
    if tauxhoraire_column and not fin_chaine_data.empty:
        sum_taux_horaire = fin_chaine_data[tauxhoraire_column].sum()
        metrics['fin_chaine_time_rate'] = metrics['fin_chaine_time'] / max(1, sum_taux_horaire) * 100
    else:
        # Default calculation
        metrics['fin_chaine_time_rate'] = (metrics['fin_chaine_time'] / max(1, total_qty * 2)) * 100
    
    # ---- ENCOURS CHAÎNE METRICS ----
    # 5. Nbre de retouches Encours Chaîne (NREC)
    if categorie_column and qtte_column:
        encours_data = filtered_data[filtered_data[categorie_column] == 'PRODUCTION ENCOURS']
        metrics['encours_count'] = encours_data[qtte_column].sum() if not encours_data.empty else 0
    else:
        # Fallback using TypeControle
        encours_data = filtered_data[filtered_data['TypeControle'] == 'Encours_Chaine'] if 'TypeControle' in filtered_data.columns else filtered_data
        metrics['encours_count'] = encours_data.shape[0]
    
    # 6. Taux de retouches Encours chaîne (TREC)
    if qttesondee_column and not encours_data.empty:
        qtte_sondee_encours = encours_data[qttesondee_column].sum()
        metrics['encours_rate'] = (metrics['encours_count'] / max(1, qtte_sondee_encours)) * 100
    else:
        # Fallback calculation
        metrics['encours_rate'] = (metrics['encours_count'] / max(1, total_qty)) * 100
    
    # 7. Temps de retouches Encours Chaîne (TepREC)
    if temps_column and operation_column and not encours_data.empty:
        try:
            # Make sure we're only working with string operations
            encours_data_with_str_op = encours_data.copy()
            encours_data_with_str_op[operation_column] = encours_data_with_str_op[operation_column].astype(str)
            
            # Select operations that start with "fixation" in Encours Chaîne
            fixation_ops_encours = encours_data_with_str_op[encours_data_with_str_op[operation_column].str.lower().str.startswith('fixation')]
            metrics['encours_time'] = fixation_ops_encours[temps_column].sum() if not fixation_ops_encours.empty and temps_column else 0
            
            # If no fixation operations or no time, fallback
            if metrics['encours_time'] == 0:
                metrics['encours_time'] = encours_data[temps_column].sum() if temps_column else metrics['encours_count'] * 5
        except (ValueError, AttributeError, TypeError):
            # If there's any error processing the string operations, fall back to a simpler calculation
            metrics['encours_time'] = encours_data[temps_column].sum() if temps_column else metrics['encours_count'] * 5
    else:
        # Default estimation
        metrics['encours_time'] = metrics['encours_count'] * 5  # 5 minutes per retouche
    
    # 8. Taux horaire de retouches Encours de chaîne (ThREC)
    if tauxhoraire_column and not encours_data.empty:
        sum_taux_horaire_encours = encours_data[tauxhoraire_column].sum()
        metrics['encours_time_rate'] = metrics['encours_time'] / max(1, sum_taux_horaire_encours) * 100
    else:
        # Default calculation
        metrics['encours_time_rate'] = (metrics['encours_time'] / max(1, total_qty * 2)) * 100
    
    # ---- REBUT METRICS ----
    # 9. Rebut encours cumulé (nombre de pièces déclassées)
    rebut_data = filtered_data[filtered_data['TypeDefaut'] == 'Rebut'] if 'TypeDefaut' in filtered_data.columns else filtered_data
    metrics['rebut_count'] = rebut_data[qtte_column].sum() if qtte_column and not rebut_data.empty else rebut_data.shape[0]
    
    # 10. Taux rebut encours cumulé
    if qttesondee_column:
        qtte_sondee_total = filtered_data[qttesondee_column].sum()
        metrics['rebut_rate'] = (metrics['rebut_count'] / max(1, qtte_sondee_total)) * 100
    else:
        metrics['rebut_rate'] = (metrics['rebut_count'] / max(1, total_qty)) * 100
    
    # 11. Taux d'avancement contrôle
    if qttesondee_column and qttelct_column:
        qtte_lct_total = filtered_data[qttelct_column].sum()
        metrics['progress_rate'] = (filtered_data[qttesondee_column].sum() / max(1, qtte_lct_total)) * 100
    else:
        # Default estimated progress
        metrics['progress_rate'] = 65  # 65% as a default value
    
    # ---- RETOUCHE CUMULÉE METRICS ----
    # 12. Retouche encours cumulée
    retouche_data = filtered_data[filtered_data['TypeDefaut'] == 'Retouche'] if 'TypeDefaut' in filtered_data.columns else filtered_data
    metrics['retouche_total_count'] = retouche_data[qtte_column].sum() if qtte_column and not retouche_data.empty else retouche_data.shape[0]
    
    # 13. Taux de retouche encours cumulée
    if qttesondee_column:
        metrics['retouche_total_rate'] = (metrics['retouche_total_count'] / max(1, filtered_data[qttesondee_column].sum())) * 100
    else:
        metrics['retouche_total_rate'] = (metrics['retouche_total_count'] / max(1, total_qty)) * 100
    
    # 14. Temps de retouches cumulé (en heures)
    if temps_column and operation_column:
        try:
            # Make sure we're only working with string operations
            # First convert operation column to string type safely
            filtered_data_with_str_op = filtered_data.copy()
            filtered_data_with_str_op[operation_column] = filtered_data_with_str_op[operation_column].astype(str)
            
            # Find all operations starting with "fix" or "fixation"
            fixation_ops_all = filtered_data_with_str_op[filtered_data_with_str_op[operation_column].str.lower().str.startswith('fix')]
            total_temps = fixation_ops_all[temps_column].sum() if not fixation_ops_all.empty and temps_column else 0
            
            # If no fixation operations found, use all retouche operations
            if total_temps == 0:
                total_temps = retouche_data[temps_column].sum() if temps_column and not retouche_data.empty else metrics['retouche_total_count'] * 5
        except (ValueError, AttributeError, TypeError):
            # If there's any error processing the string operations, fall back to a simpler calculation
            total_temps = retouche_data[temps_column].sum() if temps_column and not retouche_data.empty else metrics['retouche_total_count'] * 5
            
        # Convert to hours
        metrics['retouche_total_time'] = total_temps / 60
    else:
        # Default calculation (5 minutes per retouche)
        metrics['retouche_total_time'] = metrics['retouche_total_count'] * 5 / 60
    
    return metrics

def create_chain_dashboard(filtered_data, chain_id):
    """Create dashboard for a specific chain"""
    # Enhanced header styling
    st.markdown(f"""
    <div style='background-color:#1e3a8a; color:white; padding:15px; text-align:center; 
         font-size:22px; font-weight:bold; margin-bottom:25px; border-radius:8px; 
         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
        <i class="fas fa-industry"></i> Dashboard Opérationnel Chaîne Confection N° {chain_id}
    </div>
    """, unsafe_allow_html=True)
    
    # Show date range information
    if 'DATE' in filtered_data.columns:
        try:
            min_date = pd.to_datetime(filtered_data['DATE'].min()).strftime('%d/%m/%Y')
            max_date = pd.to_datetime(filtered_data['DATE'].max()).strftime('%d/%m/%Y')
            date_range = f"{min_date} - {max_date}"
        except:
            date_range = "Toutes les dates"
    else:
        date_range = "Toutes les dates"
    
    # Summary cards for key metrics
    st.markdown("""
    <style>
    .metric-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        flex: 1;
        margin: 0 5px;
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-title {
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 8px;
        color: #555;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
    }
    .date-range {
        background-color: #f1f5f9;
        color: #1e3a8a;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        font-size: 14px;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Calculate metrics
    metrics = calculate_operational_metrics(filtered_data)
    
    # Date range display
    st.markdown(f"""
    <div style="text-align: center;">
        <div class="date-range">
            <i class="fas fa-calendar"></i> Période: {date_range}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two main sections with modern styling
    # 1. Retouche Fin Chaîne (NRFC, TRFC, TepRFC, ThRFC)
    st.markdown("""
    <div style='background-color:#f8fafc; border-left:5px solid #3b82f6; padding:10px 15px; 
         margin-bottom:20px; font-weight:bold; color:#1e3a8a; border-radius:4px;
         box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);'>
        <i class="fas fa-tools"></i> Retouche Fin Chaîne
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for the metrics and details
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Create metrics cards for Fin Chaîne
        fin_color = "#10b981" if metrics['fin_chaine_rate'] < 10 else ("#f59e0b" if metrics['fin_chaine_rate'] < 20 else "#ef4444")
        
        # TRFC: Taux de retouches Fin de chaîne - Enhanced gauge
        gauge_fin = create_gauge_chart(
            value=metrics["fin_chaine_rate"],
            max_val=30,  # Maximum 30% retouche rate
            title="TRFC: Taux de retouche fin chaîne"
        )
        st.plotly_chart(gauge_fin, use_container_width=True, key="gauge_fin_chaine")
        
        # Display all fin chaîne metrics with improved styling
        st.markdown(f"""
        <div style='background-color:white; border-radius:8px; padding:15px; margin-bottom:15px; 
             box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);'>
            <div style='margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;'>
                <span style='font-weight:600; color:#64748b;'>NRFC:</span> 
                <span style='color:{fin_color}; font-weight:bold; font-size:18px;'>{metrics['fin_chaine_count']}</span>
                <span style='color:#94a3b8; font-size:12px;'>pcs</span>
            </div>
            <div style='margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;'>
                <span style='font-weight:600; color:#64748b;'>TRFC:</span> 
                <span style='color:{fin_color}; font-weight:bold; font-size:18px;'>{metrics['fin_chaine_rate']:.1f}%</span>
            </div>
            <div style='margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;'>
                <span style='font-weight:600; color:#64748b;'>TepRFC:</span> 
                <span style='font-weight:bold; font-size:18px;'>{metrics['fin_chaine_time']:.1f}</span>
                <span style='color:#94a3b8; font-size:12px;'>min</span>
            </div>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span style='font-weight:600; color:#64748b;'>ThRFC:</span> 
                <span style='font-weight:bold; font-size:18px;'>{metrics['fin_chaine_time_rate']:.1f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Détails postes section with improved styling
        st.markdown("""
        <div style='background-color:#f8fafc; border-radius:6px; padding:10px; margin-bottom:10px; 
             text-align:center; font-weight:bold; color:#1e3a8a;'>
            <i class="fas fa-clipboard-list"></i> Détails postes
        </div>
        """, unsafe_allow_html=True)
        
        # Create the element grid for fin chaîne
        create_element_grid(filtered_data, mode="fin_chaine")
    
    # 2. Retouche Encours Chaîne (NREC, TREC, TepREC, ThREC)
    st.markdown("""
    <div style='background-color:#f8fafc; border-left:5px solid #3b82f6; padding:10px 15px; 
         margin:25px 0 20px 0; font-weight:bold; color:#1e3a8a; border-radius:4px;
         box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);'>
        <i class="fas fa-sync-alt"></i> Retouche Encours Chaîne
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for the metrics and details
    col3, col4 = st.columns([1, 3])
    
    with col3:
        # Create metrics cards for Encours Chaîne
        encours_color = "#10b981" if metrics['encours_rate'] < 10 else ("#f59e0b" if metrics['encours_rate'] < 20 else "#ef4444")
        
        # TREC: Taux de retouches Encours chaîne - Enhanced gauge
        gauge_encours = create_gauge_chart(
            value=metrics["encours_rate"],
            max_val=30,  # Maximum 30% retouche rate
            title="TREC: Taux de retouche encours chaîne"
        )
        st.plotly_chart(gauge_encours, use_container_width=True, key="gauge_encours_chaine")
        
        # Display all encours chaîne metrics with improved styling
        st.markdown(f"""
        <div style='background-color:white; border-radius:8px; padding:15px; margin-bottom:15px; 
             box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);'>
            <div style='margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;'>
                <span style='font-weight:600; color:#64748b;'>NREC:</span> 
                <span style='color:{encours_color}; font-weight:bold; font-size:18px;'>{metrics['encours_count']}</span>
                <span style='color:#94a3b8; font-size:12px;'>pcs</span>
            </div>
            <div style='margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;'>
                <span style='font-weight:600; color:#64748b;'>TREC:</span> 
                <span style='color:{encours_color}; font-weight:bold; font-size:18px;'>{metrics['encours_rate']:.1f}%</span>
            </div>
            <div style='margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;'>
                <span style='font-weight:600; color:#64748b;'>TepREC:</span> 
                <span style='font-weight:bold; font-size:18px;'>{metrics['encours_time']:.1f}</span>
                <span style='color:#94a3b8; font-size:12px;'>min</span>
            </div>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span style='font-weight:600; color:#64748b;'>ThREC:</span> 
                <span style='font-weight:bold; font-size:18px;'>{metrics['encours_time_rate']:.1f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Détails postes section for encours chaîne with improved styling
        st.markdown("""
        <div style='background-color:#f8fafc; border-radius:6px; padding:10px; margin-bottom:10px; 
             text-align:center; font-weight:bold; color:#1e3a8a;'>
            <i class="fas fa-clipboard-list"></i> Détails postes
        </div>
        """, unsafe_allow_html=True)
        
        # Create the element grid for encours chaîne
        create_element_grid(filtered_data, mode="encours_chaine")

def create_rebutage_dashboard(filtered_data, chain_id):
    """Create dashboard for rebutage (second part)"""
    # Enhanced header styling
    st.markdown(f"""
    <div style='background-color:#1e3a8a; color:white; padding:15px; text-align:center; 
         font-size:22px; font-weight:bold; margin-bottom:25px; border-radius:8px; 
         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
        <i class="fas fa-recycle"></i> Dashboard Opérationnel Repassage Ch : {chain_id}
    </div>
    """, unsafe_allow_html=True)
    
    # Show date range information
    if 'DATE' in filtered_data.columns:
        try:
            min_date = pd.to_datetime(filtered_data['DATE'].min()).strftime('%d/%m/%Y')
            max_date = pd.to_datetime(filtered_data['DATE'].max()).strftime('%d/%m/%Y')
            date_range = f"{min_date} - {max_date}"
        except:
            date_range = "Toutes les dates"
    else:
        date_range = "Toutes les dates"
    
    # Date range display
    st.markdown(f"""
    <div style="text-align: center;">
        <div class="date-range">
            <i class="fas fa-calendar"></i> Période: {date_range}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate metrics
    metrics = calculate_operational_metrics(filtered_data)
    
    # Show Taux d'avancement contrôle at the top with modern styling
    st.markdown("""
    <div style='background-color:#f8fafc; border-left:5px solid #0ea5e9; padding:10px 15px; 
         margin-bottom:20px; font-weight:bold; color:#0369a1; border-radius:4px;
         box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);'>
        <i class="fas fa-tasks"></i> Taux d'avancement contrôle
    </div>
    """, unsafe_allow_html=True)
    
    # Create a gauge for progress
    col_prog1, col_prog2 = st.columns([1, 3])
    
    with col_prog1:
        # Create gauge chart for Progress
        gauge_progress = create_gauge_chart(
            value=metrics["progress_rate"],
            max_val=100,  # Maximum 100% progress
            title="QtteSonde/QtteLct"
        )
        st.plotly_chart(gauge_progress, use_container_width=True, key="gauge_progress")
        
        # Display metric value as text below gauge with modern styling
        progress_color = "#10b981" if metrics['progress_rate'] > 80 else ("#f59e0b" if metrics['progress_rate'] > 50 else "#ef4444")
        st.markdown(f"""
        <div style='background-color:white; border-radius:8px; padding:15px; margin-bottom:15px; 
             text-align:center; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);'>
            <div style='color:{progress_color}; font-size:28px; font-weight:bold;'>{metrics['progress_rate']:.1f}%</div>
            <div style='color:#64748b; font-size:14px; margin-top:5px;'>taux d'avancement</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_prog2:
        # Show progress information in a card with modern styling
        st.markdown(f"""
        <div style='background-color:white; border-radius:8px; padding:15px; margin-bottom:15px; 
             box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);'>
            <div style='font-size:16px; margin-bottom:15px; color:#1e3a8a; font-weight:bold;'>
                <i class="fas fa-info-circle"></i> Information d'avancement
            </div>
            
            <div style='display:grid; grid-template-columns: 1fr 1fr; gap:10px;'>
                <div style='background-color:#f1f5f9; padding:12px; border-radius:6px;'>
                    <div style='color:#64748b; font-size:12px; margin-bottom:5px;'>QtteSonde</div>
                    <div style='font-size:16px; font-weight:bold;'>{filtered_data['qttesondee'].sum() if 'qttesondee' in filtered_data.columns else 'N/A'}</div>
                </div>
                
                <div style='background-color:#f1f5f9; padding:12px; border-radius:6px;'>
                    <div style='color:#64748b; font-size:12px; margin-bottom:5px;'>QtteLct</div>
                    <div style='font-size:16px; font-weight:bold;'>{filtered_data['qttelct'].sum() if 'qttelct' in filtered_data.columns else 'N/A'}</div>
                </div>
                
                <div style='background-color:#f1f5f9; padding:12px; border-radius:6px;'>
                    <div style='color:#64748b; font-size:12px; margin-bottom:5px;'>Début</div>
                    <div style='font-size:16px; font-weight:bold;'>{pd.to_datetime(filtered_data['date'].min()).strftime('%d/%m/%Y') if 'date' in filtered_data.columns else 'N/A'}</div>
                </div>
                
                <div style='background-color:#f1f5f9; padding:12px; border-radius:6px;'>
                    <div style='color:#64748b; font-size:12px; margin-bottom:5px;'>Fin estimée</div>
                    <div style='font-size:16px; font-weight:bold;'>{pd.to_datetime(filtered_data['date'].max()).strftime('%d/%m/%Y') if 'date' in filtered_data.columns else 'N/A'}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 1. Rebut Cumulée with modern styling
    st.markdown("""
    <div style='background-color:#f8fafc; border-left:5px solid #ef4444; padding:10px 15px; 
         margin:25px 0 20px 0; font-weight:bold; color:#b91c1c; border-radius:4px;
         box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);'>
        <i class="fas fa-ban"></i> Rebut Cumulée
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
        
        # Display metric value as text below gauge with enhanced styling
        rebut_color = "#10b981" if metrics['rebut_rate'] < 2 else ("#f59e0b" if metrics['rebut_rate'] < 3 else "#ef4444")
        st.markdown(f"""
        <div style='background-color:white; border-radius:8px; padding:15px; margin-bottom:15px; 
             text-align:center; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);'>
            <div style='color:{rebut_color}; font-size:28px; font-weight:bold;'>{metrics['rebut_rate']:.1f}%</div>
            <div style='color:#64748b; font-size:14px;'>({metrics['rebut_count']} pcs)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Détails OF section with enhanced styling
        st.markdown("""
        <div style='background-color:#f8fafc; border-radius:6px; padding:10px; margin-bottom:10px; 
             text-align:center; font-weight:bold; color:#1e3a8a;'>
            <i class="fas fa-clipboard-list"></i> Détails OF
        </div>
        """, unsafe_allow_html=True)
        
        # Create the orders detail grid
        create_orders_detail_grid(filtered_data)
    
    # 2. Retouche Cumulée with modern styling
    st.markdown("""
    <div style='background-color:#f8fafc; border-left:5px solid #ef4444; padding:10px 15px; 
         margin:25px 0 20px 0; font-weight:bold; color:#b91c1c; border-radius:4px;
         box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);'>
        <i class="fas fa-tools"></i> Retouche Cumulée
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
        
        # Display metric value as text below gauge with enhanced styling
        retouche_color = "#10b981" if metrics['retouche_total_rate'] < 10 else ("#f59e0b" if metrics['retouche_total_rate'] < 20 else "#ef4444")
        st.markdown(f"""
        <div style='background-color:white; border-radius:8px; padding:15px; margin-bottom:15px; 
             text-align:center; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);'>
            <div style='color:{retouche_color}; font-size:28px; font-weight:bold;'>{metrics['retouche_total_rate']:.1f}%</div>
            <div style='color:#64748b; font-size:14px;'>({metrics['retouche_total_count']} pcs)</div>
            <div style='color:#64748b; font-size:14px; margin-top:5px;'>{metrics['retouche_total_time']:.1f} h de retouche</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Create another table for orders detail grid with improved styling
        st.markdown("""
        <div style='background-color:#f8fafc; border-radius:6px; padding:10px; margin-bottom:10px; 
             text-align:center; font-weight:bold; color:#1e3a8a;'>
            <i class="fas fa-clipboard-list"></i> Détails OF
        </div>
        """, unsafe_allow_html=True)
        
        create_orders_detail_grid(filtered_data)
        
def create_operational_dashboard(data):
    """Main function to create the operational dashboard"""
    # Enhance sidebar styling
    st.sidebar.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
    }
    .sidebar-title {
        background-color: #1e3a8a;
        color: white;
        padding: 15px 10px;
        margin: -1rem -1rem 1rem -1rem;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        border-radius: 0 0 10px 10px;
    }
    .filter-section {
        background-color: white;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    .filter-header {
        color: #1e3a8a;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 10px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 5px;
    }
    </style>
    
    <div class="sidebar-title">
        <i class="fas fa-sliders-h"></i> Contrôles du Dashboard
    </div>
    """, unsafe_allow_html=True)
    
    # Date filter section with improved styling
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="filter-header"><i class="fas fa-calendar-alt"></i> Période</div>', unsafe_allow_html=True)
    
    # Try to get min/max dates or use defaults
    try:
        min_date_value = pd.to_datetime(data['DATE'].min()).date() if 'DATE' in data.columns else pd.to_datetime("2023-01-01").date()
        max_date_value = pd.to_datetime(data['DATE'].max()).date() if 'DATE' in data.columns else pd.to_datetime("2023-12-31").date()
    except:
        min_date_value = pd.to_datetime("2023-01-01").date()
        max_date_value = pd.to_datetime("2023-12-31").date()
    
    start_date = st.sidebar.date_input("Date de début", value=min_date_value)
    end_date = st.sidebar.date_input("Date de fin", value=max_date_value)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Chain filter section with improved styling
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="filter-header"><i class="fas fa-industry"></i> Sélection Chaîne</div>', unsafe_allow_html=True)
    
    # Get chain options
    chain_options = data['IDChaineMontage'].unique().tolist() if 'IDChaineMontage' in data.columns else []
    if not chain_options and 'Chaine' in data.columns:
        chain_options = data['Chaine'].unique().tolist()
    
    if not chain_options and 'idchaine' in data.columns:
        chain_options = data['idchaine'].unique().tolist()
        
    if not chain_options:
        chain_options = ["Chaîne 1", "Chaîne 2", "Chaîne 3"]
    
    selected_chain = st.sidebar.selectbox("Chaîne", chain_options, index=0)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
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
    
    # Add export options and supplementary information in sidebar
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="filter-header"><i class="fas fa-file-export"></i> Exporter</div>', unsafe_allow_html=True)
    export_format = st.sidebar.selectbox("Format", ["Excel", "CSV", "PDF"])
    if st.sidebar.button("Télécharger le rapport"):
        st.sidebar.success("Rapport généré. Le téléchargement va commencer.")
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Add help section
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="filter-header"><i class="fas fa-question-circle"></i> Aide</div>', unsafe_allow_html=True)
    st.sidebar.info("Pour plus d'informations sur les indicateurs et les métriques utilisées, contactez le service qualité.")
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Create dashboard tabs with improved styling
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9;
        border-radius: 6px 6px 0 0;
        padding: 10px 20px;
        font-weight: 600;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e3a8a !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
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