import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import apply_date_filter, apply_categorical_filter, apply_numerical_filter, apply_all_filters
import html

def create_gauge_chart(value, max_val=100, title="Gauge Chart"):
    """Create a gauge chart for KPI visualization"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 16, 'color': '#1e40af'}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "#1e40af"},
            'bar': {'color': "#3b82f6"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, max_val * 0.33], 'color': '#dbeafe'},
                {'range': [max_val * 0.33, max_val * 0.67], 'color': '#93c5fd'},
                {'range': [max_val * 0.67, max_val], 'color': '#60a5fa'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.8
            }
        }
    ))
    
    # Update layout
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=30, b=20),
        font=dict(family="Arial", size=12)
    )
    
    return fig

def create_bar_chart(data, x_col, y_col, title="Top Operations", color_discrete_sequence=None):
    """Create a bar chart for top operations or other metrics"""
    if data.empty or x_col not in data.columns or y_col not in data.columns:
        # Return empty chart with message
        fig = go.Figure()
        fig.update_layout(
            title=title + " - Aucune donnée disponible",
            height=300,
            annotations=[dict(
                text="Aucune donnée disponible pour ce graphique",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5
            )]
        )
        return fig
    
    # Group and aggregate data if needed
    if len(data) > 10:
        # Group by x_col and sum y_col values
        grouped = data.groupby(x_col)[y_col].sum().reset_index()
        # Sort by y_col descending
        grouped = grouped.sort_values(by=y_col, ascending=False)
        # Take top 10
        plot_data = grouped.head(10)
    else:
        # Sort the original data
        plot_data = data.sort_values(by=y_col, ascending=False)
    
    # Create the bar chart
    colors = color_discrete_sequence or ["#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe"]
    fig = px.bar(
        plot_data,
        x=x_col,
        y=y_col,
        title=title,
        color_discrete_sequence=colors,
        text=y_col,
        labels={x_col: x_col.replace("ID", ""), y_col: y_col.replace("ID", "")}
    )
    
    # Format the text labels
    fig.update_traces(
        texttemplate='%{text:.2f}',
        textposition='auto',
        marker_line_color='#e2e8f0',
        marker_line_width=1
    )
    
    # Update layout
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=100),
        xaxis=dict(
            tickangle=-45,
            title="",
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor='#f1f5f9'
        ),
        plot_bgcolor="white"
    )
    
    return fig

def create_pie_chart(data, names, values, title="Distribution", color_discrete_sequence=None):
    """Create a pie chart for distribution metrics"""
    if data.empty or names not in data.columns or values not in data.columns:
        # Return empty chart with message
        fig = go.Figure()
        fig.update_layout(
            title=title + " - Aucune donnée disponible",
            height=300,
            annotations=[dict(
                text="Aucune donnée disponible pour ce graphique",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5
            )]
        )
        return fig
    
    # Group by names and sum values
    grouped = data.groupby(names)[values].sum().reset_index()
    
    # Sort by values descending
    grouped = grouped.sort_values(by=values, ascending=False)
    
    # Limit to top 6 and group the rest as "Autres"
    if len(grouped) > 6:
        top = grouped.head(5)
        others_value = grouped.iloc[5:][values].sum()
        others = pd.DataFrame({names: ["Autres"], values: [others_value]})
        plot_data = pd.concat([top, others])
    else:
        plot_data = grouped
    
    # Create the pie chart
    colors = color_discrete_sequence or px.colors.qualitative.Set2
    fig = px.pie(
        plot_data,
        names=names,
        values=values,
        title=title,
        color_discrete_sequence=colors,
        hole=0.4,  # Donut chart
        labels={names: names.replace("ID", ""), values: values.replace("ID", "")}
    )
    
    # Add percentage to labels
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=10,
        marker=dict(line=dict(color='#FFFFFF', width=1))
    )
    
    # Update layout
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        )
    )
    
    # Add total value in center
    total = plot_data[values].sum()
    fig.add_annotation(
        text=f"Total<br>{total:.0f}",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=12, color="#1e40af")
    )
    
    return fig

def create_cards_grid(filtered_data, column_name, count_col='count', top_n=12):
    """Create a grid of cards for operations or other categories"""
    # Group by column_name and count occurrences
    if column_name not in filtered_data.columns:
        return st.warning(f"Colonne '{column_name}' non trouvée dans les données.")
    
    # If count_col exists, use sum of that column, otherwise count rows
    if count_col in filtered_data.columns:
        grouped = filtered_data.groupby(column_name)[count_col].sum().reset_index()
    else:
        grouped = filtered_data.groupby(column_name).size().reset_index(name='count')
        count_col = 'count'
    
    # Sort by count descending and get top N
    grouped = grouped.sort_values(by=count_col, ascending=False).head(top_n)
    
    # Calculate total for percentages
    total = grouped[count_col].sum()
    
    # Calculate percentages and add visual indicators
    grouped['percentage'] = (grouped[count_col] / total * 100).round(1)
    
    # Create a color scale based on percentage
    max_percentage = grouped['percentage'].max()
    grouped['color_intensity'] = (grouped['percentage'] / max_percentage).round(2)
    
    # Create the grid with 3 or 4 cards per row
    cols_per_row = 4 if len(grouped) >= 8 else 3
    
    # Create rows
    for i in range(0, len(grouped), cols_per_row):
        row_data = grouped.iloc[i:i+cols_per_row]
        cols = st.columns(cols_per_row)
        
        for j, (_, item) in enumerate(row_data.iterrows()):
            if j < len(cols):
                with cols[j]:
                    # Calculate background color based on intensity
                    bg_color = f"rgba(59, 130, 246, {item['color_intensity'] * 0.3})"
                    
                    st.markdown(
                        f"""
                        <div style="background-color: {bg_color}; border-radius: 10px; padding: 15px; height: 100px; position: relative;">
                            <div style="font-size: 14px; font-weight: 600; margin-bottom: 10px; height: 40px; overflow: hidden;">{item[column_name]}</div>
                            <div style="font-size: 20px; font-weight: 700; color: #1e40af;">{item[count_col]}</div>
                            <div style="font-size: 12px; color: #64748b; position: absolute; bottom: 15px;">{item['percentage']}% du total</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

def calculate_metrics(filtered_data):
    """Calculate operational metrics from the data"""
    metrics = {}
    
    # Case-insensitive column name matching and alias handling
    def get_column(possible_names, default=None):
        for name in possible_names:
            # Try exact match
            if name in filtered_data.columns:
                return name
            # Try case-insensitive match
            for col in filtered_data.columns:
                if col.lower() == name.lower():
                    return col
        return default
    
    # Apply category filter function helper
    def filter_by_category(category_values):
        category_col = get_column(['Categorie', 'categorie', 'CategoryType'])
        if category_col:
            if isinstance(category_values, str):
                category_values = [category_values]
            return filtered_data[filtered_data[category_col].isin(category_values)]
        return pd.DataFrame()
    
    # Find critical columns using multiple potential names
    categorie_column = get_column(['Categorie', 'categorie', 'CategoryType'])
    qtte_column = get_column(['Qtte', 'qtte', 'Quantite', 'NbrReclamations'])
    qttesondee_column = get_column(['QtteSondee', 'qttesondee'])
    qttelct_column = get_column(['QtteLct', 'qttelct'])
    temps_column = get_column(['Temps', 'temps', 'TempsRetouche'])
    taux_horaire_column = get_column(['TauxHoraire', 'tauxhoraire'])
    operation_column = get_column(['Operation', 'operation', 'IDOperation', 'idoperation', 'Libelle'])
    type_defaut_column = get_column(['TypeDefaut', 'typedefaut', 'DefautType', 'CodeDefaut'])
    chaine_column = get_column(['IDChaineMontage', 'idchainemontage', 'IDChaine', 'idchaine', 'Chaine'])
    
    # Calculate metrics for "Fin Chaîne"
    fin_chaine = filter_by_category(['PRODUCTION FIN CHAINE', 'Production Fin Chaine', 'Fin Chaine'])
    if not fin_chaine.empty and qtte_column:
        metrics['NRFC'] = fin_chaine[qtte_column].sum()
    else:
        metrics['NRFC'] = 0
    
    if not fin_chaine.empty and temps_column:
        metrics['ThRFC'] = fin_chaine[temps_column].sum()
    else:
        metrics['ThRFC'] = 0
    
    if not fin_chaine.empty and qttesondee_column:
        metrics['QtteSondeFC'] = fin_chaine[qttesondee_column].sum()
        if metrics['QtteSondeFC'] > 0:
            metrics['TRFC'] = (metrics['NRFC'] / metrics['QtteSondeFC']) * 100
        else:
            metrics['TRFC'] = 0
    else:
        metrics['QtteSondeFC'] = 0
        metrics['TRFC'] = 0
    
    if not fin_chaine.empty and temps_column and taux_horaire_column and qtte_column:
        # Calculate cost
        temps_total = fin_chaine[temps_column].sum() / 60  # Convert to hours
        taux_moyen = fin_chaine[taux_horaire_column].mean()
        metrics['TepRFC'] = temps_total * taux_moyen
    else:
        metrics['TepRFC'] = 0
    
    # Calculate metrics for "Encours Chaîne"
    encours_chaine = filter_by_category(['PRODUCTION ENCOURS', 'Production Encours', 'Encours Chaine'])
    if not encours_chaine.empty and qtte_column:
        metrics['NREC'] = encours_chaine[qtte_column].sum()
    else:
        metrics['NREC'] = 0
    
    if not encours_chaine.empty and temps_column:
        metrics['ThREC'] = encours_chaine[temps_column].sum()
    else:
        metrics['ThREC'] = 0
    
    if not encours_chaine.empty and qttesondee_column:
        metrics['QtteSondeEC'] = encours_chaine[qttesondee_column].sum()
        if metrics['QtteSondeEC'] > 0:
            metrics['TREC'] = (metrics['NREC'] / metrics['QtteSondeEC']) * 100
        else:
            metrics['TREC'] = 0
    else:
        metrics['QtteSondeEC'] = 0
        metrics['TREC'] = 0
    
    if not encours_chaine.empty and temps_column and taux_horaire_column and qtte_column:
        # Calculate cost
        temps_total = encours_chaine[temps_column].sum() / 60  # Convert to hours
        taux_moyen = encours_chaine[taux_horaire_column].mean()
        metrics['TepREC'] = temps_total * taux_moyen
    else:
        metrics['TepREC'] = 0
    
    # Calculate Rebut metrics
    rebut_data = pd.DataFrame()
    if type_defaut_column:
        rebut_terms = ['Rebut', 'rebut', 'REBUT']
        mask = filtered_data[type_defaut_column].astype(str).str.contains('|'.join(rebut_terms), case=False)
        rebut_data = filtered_data[mask]
    
    # Calculate Rebut metrics
    if not rebut_data.empty and qtte_column:
        metrics['NbRebut'] = rebut_data[qtte_column].sum()
    else:
        metrics['NbRebut'] = 0
    
    if qttelct_column:
        metrics['QtteLct'] = filtered_data[qttelct_column].sum()
        if metrics['QtteLct'] > 0:
            metrics['TauxRebut'] = (metrics['NbRebut'] / metrics['QtteLct']) * 100
        else:
            metrics['TauxRebut'] = 0
    else:
        metrics['QtteLct'] = 0
        metrics['TauxRebut'] = 0
    
    if qttelct_column and qttesondee_column:
        metrics['QtteLct'] = filtered_data[qttelct_column].sum()
        metrics['QtteSondeTotal'] = filtered_data[qttesondee_column].sum()
        if metrics['QtteLct'] > 0:
            metrics['TauxAvancement'] = (metrics['QtteSondeTotal'] / metrics['QtteLct']) * 100
        else:
            metrics['TauxAvancement'] = 0
    else:
        metrics['QtteLct'] = 0
        metrics['QtteSondeTotal'] = 0
        metrics['TauxAvancement'] = 0
    
    # Calculate total metrics
    metrics['NbTotal'] = metrics['NRFC'] + metrics['NREC'] + metrics['NbRebut']
    metrics['ThTotal'] = metrics['ThRFC'] + metrics['ThREC']
    metrics['TepTotal'] = metrics['TepRFC'] + metrics['TepREC']
    
    return metrics

def display_metric_card(title, value, unit="", color="blue", description="", icon="📊"):
    """Display a metric in a styled card with proper formatting"""
    # Format value based on type
    if isinstance(value, float):
        if abs(value) < 0.01:
            formatted_value = f"{value:.6f}{unit}"
        elif abs(value) < 1:
            formatted_value = f"{value:.4f}{unit}"
        elif abs(value) < 10:
            formatted_value = f"{value:.2f}{unit}"
        else:
            formatted_value = f"{value:.1f}{unit}"
    else:
        formatted_value = f"{value:,}{unit}"
    
    # Define color style
    if color == "blue":
        bg_color = "#dbeafe"
        text_color = "#1e40af"
        value_color = "#1e40af"
    elif color == "green":
        bg_color = "#d1fae5"
        text_color = "#047857"
        value_color = "#047857"
    elif color == "red":
        bg_color = "#fee2e2"
        text_color = "#b91c1c"
        value_color = "#b91c1c"
    elif color == "yellow":
        bg_color = "#fef3c7"
        text_color = "#92400e"
        value_color = "#92400e"
    else:
        bg_color = "#f3f4f6"
        text_color = "#374151"
        value_color = "#374151"
    
    st.markdown(
        f"""
        <div style="background-color: {bg_color}; border-radius: 10px; padding: 20px; height: 100%;">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="font-size: 20px; margin-right: 8px;">{icon}</div>
                <div style="font-size: 14px; color: {text_color}; font-weight: 600;">{title}</div>
            </div>
            <div style="font-size: 24px; font-weight: 700; color: {value_color}; margin-bottom: 5px;">{formatted_value}</div>
            <div style="font-size: 12px; color: {text_color}; opacity: 0.8;">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def create_operational_dashboard(data):
    """Create a complete operational dashboard with metrics and visualizations"""
    # Add custom CSS for dashboard styling
    st.markdown("""
    <style>
    .dashboard-title {
        font-size: 24px;
        font-weight: bold;
        color: #1e40af;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid #e2e8f0;
    }
    .section-title {
        font-size: 18px;
        font-weight: bold;
        color: #1e40af;
        margin: 15px 0;
        padding: 8px 0;
        border-left: 4px solid #1e40af;
        padding-left: 10px;
        background-color: #f8fafc;
    }
    .filter-container {
        background-color: #f8fafc;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Dashboard Title
    st.markdown("<div class='dashboard-title'>🏭 Dashboard Opérationnel</div>", unsafe_allow_html=True)
    
    # Filters section
    st.markdown("<div class='section-title'>🔍 Filtres</div>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Date Filter
            date_col = next((col for col in data.columns if col.lower() in ['date', 'datetime']), None)
            if date_col:
                min_date = data[date_col].min()
                max_date = data[date_col].max()
                try:
                    start_date = st.date_input("Date début:", min_date)
                    end_date = st.date_input("Date fin:", max_date)
                except:
                    # If date conversion fails, use string representation
                    st.warning("Format de date non reconnu, utilisez les autres filtres.")
                    start_date = None
                    end_date = None
            else:
                st.warning("Colonne de date non trouvée")
                start_date = None
                end_date = None
        
        with col2:
            # Chain Filter
            chain_cols = [col for col in data.columns if col.lower() in ['idchainemontage', 'chaine', 'idchaine']]
            if chain_cols:
                chain_col = chain_cols[0]
                chain_options = ["Tous"] + sorted([str(x) for x in data[chain_col].dropna().unique()])
                selected_chain = st.selectbox("Chaîne:", chain_options)
            else:
                st.warning("Colonne de chaîne non trouvée")
                selected_chain = "Tous"
        
        with col3:
            # Operation Filter
            operation_cols = [col for col in data.columns if col.lower() in ['operation', 'idoperation', 'libelle']]
            if operation_cols:
                operation_col = operation_cols[0]
                operation_options = ["Tous"] + sorted([str(x) for x in data[operation_col].dropna().unique() if str(x).strip()])
                selected_operation = st.selectbox("Opération:", operation_options)
            else:
                st.warning("Colonne d'opération non trouvée")
                selected_operation = "Tous"
    
    # Add more filters in an expander
    with st.expander("Filtres avancés"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Type Filter
            type_cols = [col for col in data.columns if col.lower() in ['typedefaut', 'defauttype', 'codedefaut']]
            if type_cols:
                type_col = type_cols[0]
                type_options = ["Tous"] + sorted([str(x) for x in data[type_col].dropna().unique() if str(x).strip()])
                selected_type = st.selectbox("Type de défaut:", type_options)
            else:
                st.warning("Colonne de type non trouvée")
                selected_type = "Tous"
        
        with col2:
            # Controller Filter
            controller_cols = [col for col in data.columns if col.lower() in ['controleur', 'idcontroleur']]
            if controller_cols:
                controller_col = controller_cols[0]
                controller_options = ["Tous"] + sorted([str(x) for x in data[controller_col].dropna().unique() if str(x).strip()])
                selected_controller = st.selectbox("Contrôleur:", controller_options)
            else:
                st.warning("Colonne de contrôleur non trouvée")
                selected_controller = "Tous"
    
    # Apply filters to data
    filtered_data = data.copy()
    
    # Apply date filter
    if date_col and start_date and end_date:
        filtered_data = apply_date_filter(filtered_data, start_date, end_date, date_col)
    
    # Apply chain filter
    if chain_cols and selected_chain != "Tous":
        chain_col = chain_cols[0]
        filtered_data = apply_categorical_filter(filtered_data, chain_col, [selected_chain])
    
    # Apply operation filter
    if operation_cols and selected_operation != "Tous":
        operation_col = operation_cols[0]
        filtered_data = apply_categorical_filter(filtered_data, operation_col, [selected_operation])
    
    # Apply type filter
    if type_cols and selected_type != "Tous":
        type_col = type_cols[0]
        filtered_data = apply_categorical_filter(filtered_data, type_col, [selected_type])
    
    # Apply controller filter
    if controller_cols and selected_controller != "Tous":
        controller_col = controller_cols[0]
        filtered_data = apply_categorical_filter(filtered_data, controller_col, [selected_controller])
    
    # Check if the filtered data is empty
    if filtered_data.empty:
        st.warning("Aucune donnée ne correspond aux filtres sélectionnés. Veuillez ajuster vos filtres.")
        return
    
    # Calculate metrics for filtered data
    metrics = calculate_metrics(filtered_data)
    
    # ===== Dashboard Sections =====
    
    # Create tabs for different dashboard sections
    tab1, tab2, tab3 = st.tabs(["Fin Chaîne", "Encours Chaîne", "Rebut"])
    
    # TAB 1: "Fin Chaîne" Dashboard
    with tab1:
        st.markdown("<div class='section-title'>📊 Métriques Fin Chaîne</div>", unsafe_allow_html=True)
        
        # First row of metrics
        cols = st.columns(4)
        
        with cols[0]:
            display_metric_card("Nombre de retouches", metrics['NRFC'], "", "blue", "Total des retouches en fin de chaîne", "🔢")
        
        with cols[1]:
            display_metric_card("Taux de retouches", metrics['TRFC'], "%", "red", "Pourcentage de pièces retouchées", "📈")
        
        with cols[2]:
            display_metric_card("Temps de retouche", metrics['ThRFC'], " min", "yellow", "Temps total de retouche", "⏱️")
        
        with cols[3]:
            display_metric_card("Coût de retouche", metrics['TepRFC'], " €", "red", "Coût estimé des retouches", "💰")
        
        # Visualization section
        st.markdown("<div class='section-title'>📊 Visualisations Fin Chaîne</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Filter data for Fin Chaîne
            categorie_column = next((col for col in filtered_data.columns if col.lower() in ['categorie', 'categorytype']), None)
            if categorie_column:
                fin_chaine_data = filtered_data[filtered_data[categorie_column].str.contains('Fin Chaîne|FIN CHAINE', case=False, na=False)]
            else:
                fin_chaine_data = filtered_data
            
            # Create gauge chart for TRFC
            gauge_chart = create_gauge_chart(metrics['TRFC'], 20, "Taux de retouche fin chaîne (%)")
            st.plotly_chart(gauge_chart, use_container_width=True)
        
        with col2:
            # Get columns for operation and quantity
            operation_col = next((col for col in filtered_data.columns if col.lower() in ['operation', 'idoperation', 'libelle']), None)
            qtte_col = next((col for col in filtered_data.columns if col.lower() in ['qtte', 'quantite', 'nbrreclamations']), None)
            
            if operation_col and qtte_col and not fin_chaine_data.empty:
                # Create bar chart for top operations
                bar_chart = create_bar_chart(
                    fin_chaine_data,
                    operation_col,
                    qtte_col,
                    "Top opérations avec le plus de retouches"
                )
                st.plotly_chart(bar_chart, use_container_width=True)
            else:
                st.info("Données insuffisantes pour afficher les graphiques")
        
        # Detail Section
        st.markdown("<div class='section-title'>📋 Détails des opérations Fin Chaîne</div>", unsafe_allow_html=True)
        
        # Create operation cards grid if operation column exists
        operation_col = next((col for col in filtered_data.columns if col.lower() in ['operation', 'idoperation', 'libelle']), None)
        if operation_col and not fin_chaine_data.empty:
            create_cards_grid(fin_chaine_data, operation_col)
        else:
            st.info("Aucune donnée d'opération disponible pour Fin Chaîne")
    
    # TAB 2: "Encours Chaîne" Dashboard
    with tab2:
        st.markdown("<div class='section-title'>📊 Métriques Encours Chaîne</div>", unsafe_allow_html=True)
        
        # First row of metrics
        cols = st.columns(4)
        
        with cols[0]:
            display_metric_card("Nombre de retouches", metrics['NREC'], "", "blue", "Total des retouches en cours de chaîne", "🔢")
        
        with cols[1]:
            display_metric_card("Taux de retouches", metrics['TREC'], "%", "red", "Pourcentage de pièces retouchées", "📈")
        
        with cols[2]:
            display_metric_card("Temps de retouche", metrics['ThREC'], " min", "yellow", "Temps total de retouche", "⏱️")
        
        with cols[3]:
            display_metric_card("Coût de retouche", metrics['TepREC'], " €", "red", "Coût estimé des retouches", "💰")
        
        # Visualization section
        st.markdown("<div class='section-title'>📊 Visualisations Encours Chaîne</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Filter data for Encours Chaîne
            categorie_column = next((col for col in filtered_data.columns if col.lower() in ['categorie', 'categorytype']), None)
            if categorie_column:
                encours_chaine_data = filtered_data[filtered_data[categorie_column].str.contains('Encours|ENCOURS', case=False, na=False)]
            else:
                encours_chaine_data = filtered_data
            
            # Create gauge chart for TREC
            gauge_chart = create_gauge_chart(metrics['TREC'], 20, "Taux de retouche encours chaîne (%)")
            st.plotly_chart(gauge_chart, use_container_width=True)
        
        with col2:
            # Get columns for operation and quantity
            operation_col = next((col for col in filtered_data.columns if col.lower() in ['operation', 'idoperation', 'libelle']), None)
            qtte_col = next((col for col in filtered_data.columns if col.lower() in ['qtte', 'quantite', 'nbrreclamations']), None)
            
            if operation_col and qtte_col and not encours_chaine_data.empty:
                # Create bar chart for top operations
                bar_chart = create_bar_chart(
                    encours_chaine_data,
                    operation_col,
                    qtte_col,
                    "Top opérations avec le plus de retouches"
                )
                st.plotly_chart(bar_chart, use_container_width=True)
            else:
                st.info("Données insuffisantes pour afficher les graphiques")
        
        # Detail Section
        st.markdown("<div class='section-title'>📋 Détails des opérations Encours Chaîne</div>", unsafe_allow_html=True)
        
        # Create operation cards grid if operation column exists
        operation_col = next((col for col in filtered_data.columns if col.lower() in ['operation', 'idoperation', 'libelle']), None)
        if operation_col and not encours_chaine_data.empty:
            create_cards_grid(encours_chaine_data, operation_col)
        else:
            st.info("Aucune donnée d'opération disponible pour Encours Chaîne")
    
    # TAB 3: "Rebut" Dashboard
    with tab3:
        st.markdown("<div class='section-title'>📊 Métriques Rebut</div>", unsafe_allow_html=True)
        
        # First row of metrics
        cols = st.columns(3)
        
        with cols[0]:
            display_metric_card("Nombre de rebuts", metrics['NbRebut'], "", "red", "Total des pièces rebutées", "🗑️")
        
        with cols[1]:
            display_metric_card("Taux de rebut", metrics['TauxRebut'], "%", "red", "Pourcentage de pièces rebutées", "📉")
        
        with cols[2]:
            display_metric_card("Taux d'avancement contrôle", metrics['TauxAvancement'], "%", "green", "QtteSonde/QtteLct", "🔍")
        
        # Visualization section
        st.markdown("<div class='section-title'>📊 Visualisations Rebut</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Filter data for Rebut
            type_defaut_column = next((col for col in filtered_data.columns if col.lower() in ['typedefaut', 'defauttype', 'codedefaut']), None)
            if type_defaut_column:
                rebut_data = filtered_data[filtered_data[type_defaut_column].str.contains('Rebut|REBUT', case=False, na=False)]
            else:
                rebut_data = filtered_data
            
            # Create gauge chart for TauxRebut
            gauge_chart = create_gauge_chart(metrics['TauxRebut'], 10, "Taux de rebut (%)")
            st.plotly_chart(gauge_chart, use_container_width=True)
        
        with col2:
            # Get columns for operation and quantity
            type_defaut_column = next((col for col in filtered_data.columns if col.lower() in ['typedefaut', 'defauttype', 'codedefaut']), None)
            qtte_col = next((col for col in filtered_data.columns if col.lower() in ['qtte', 'quantite', 'nbrreclamations']), None)
            
            if type_defaut_column and qtte_col and not rebut_data.empty:
                # Create pie chart for rebut reasons
                pie_chart = create_pie_chart(
                    rebut_data,
                    type_defaut_column,
                    qtte_col,
                    "Distribution des raisons de rebut"
                )
                st.plotly_chart(pie_chart, use_container_width=True)
            else:
                st.info("Données insuffisantes pour afficher les graphiques")
        
        # Additional Rebut Details
        st.markdown("<div class='section-title'>📋 Détails des rebuts par ordre de fabrication</div>", unsafe_allow_html=True)
        
        # Get OF column
        of_column = next((col for col in filtered_data.columns if col.lower() in ['idofabrication', 'ofab', 'of']), None)
        
        if of_column and type_defaut_column and not rebut_data.empty:
            # Group by OF and count rebuts
            of_rebuts = rebut_data.groupby(of_column)[qtte_col].sum().reset_index()
            of_rebuts = of_rebuts.sort_values(by=qtte_col, ascending=False).head(10)
            
            # Show the top OF with rebuts
            st.dataframe(
                of_rebuts.rename(columns={of_column: "Ordre de fabrication", qtte_col: "Nombre de rebuts"}),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Aucune donnée de rebut par ordre de fabrication disponible")
    
    # Additional Global Metrics Section
    st.markdown("<div class='section-title'>📊 Métriques Globales</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Create combined metrics card
        st.markdown(
            f"""
            <div style="background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <div style="font-size: 16px; font-weight: 600; color: #1e40af; margin-bottom: 15px;">Vue d'ensemble des retouches</div>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: 600;">Métrique</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: 600; text-align: right;">Fin Chaîne</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: 600; text-align: right;">Encours</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: 600; text-align: right;">Total</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">Nombre</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: right;">{metrics['NRFC']:.0f}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: right;">{metrics['NREC']:.0f}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: 600;">{metrics['NRFC'] + metrics['NREC']:.0f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">Temps (min)</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: right;">{metrics['ThRFC']:.0f}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: right;">{metrics['ThREC']:.0f}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: 600;">{metrics['ThTotal']:.0f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">Coût (€)</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: right;">{metrics['TepRFC']:.2f}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: right;">{metrics['TepREC']:.2f}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: 600;">{metrics['TepTotal']:.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">Taux (%)</td>
                        <td style="padding: 8px; text-align: right;">{metrics['TRFC']:.2f}%</td>
                        <td style="padding: 8px; text-align: right;">{metrics['TREC']:.2f}%</td>
                        <td style="padding: 8px; text-align: right; font-weight: 600;">-</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        # Check for necessary columns
        chain_column = next((col for col in filtered_data.columns if col.lower() in ['idchainemontage', 'idchaine', 'chaine']), None)
        qtte_col = next((col for col in filtered_data.columns if col.lower() in ['qtte', 'quantite', 'nbrreclamations']), None)
        
        if chain_column and qtte_col and not filtered_data.empty:
            # Create pie chart for distribution by chain
            pie_chart = create_pie_chart(
                filtered_data,
                chain_column,
                qtte_col,
                "Distribution par chaîne"
            )
            st.plotly_chart(pie_chart, use_container_width=True)
        else:
            st.info("Données insuffisantes pour afficher la distribution par chaîne")
    
    with col3:
        # Check for necessary columns
        controller_column = next((col for col in filtered_data.columns if col.lower() in ['controleur', 'idcontroleur']), None)
        qtte_col = next((col for col in filtered_data.columns if col.lower() in ['qtte', 'quantite', 'nbrreclamations']), None)
        
        if controller_column and qtte_col and not filtered_data.empty:
            # Create bar chart for top controllers
            bar_chart = create_bar_chart(
                filtered_data,
                controller_column,
                qtte_col,
                "Top contrôleurs"
            )
            st.plotly_chart(bar_chart, use_container_width=True)
        else:
            st.info("Données insuffisantes pour afficher les top contrôleurs")
    
    # Footer
    st.markdown("""
    <div style="margin-top: 40px; padding: 15px; text-align: center; color: #64748b; border-top: 1px solid #e2e8f0;">
        <p>Dashboard Opérationnel v2.0 - Dernière mise à jour: Mars 2025</p>
    </div>
    """, unsafe_allow_html=True)