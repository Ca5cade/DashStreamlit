import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import apply_date_filter, apply_categorical_filter, apply_numerical_filter, apply_all_filters
import html

def create_kpi_card(title, value, previous_value=None, target=None, unit="", is_percentage=False):
    """Create a KPI card with title, value, and optional comparison to previous value"""
    # Format value based on type and is_percentage flag
    formatted_target = ""  # Initialize formatted_target
    if is_percentage:
        formatted_value = f"{value:.1f}%"
        if previous_value is not None:
            formatted_previous = f"{previous_value:.1f}%"
        if target is not None:
            formatted_target = f"{target:.1f}%"
    elif isinstance(value, float):
        formatted_value = f"{value:.1f}{unit}"
        if previous_value is not None:
            formatted_previous = f"{previous_value:.1f}{unit}"
        if target is not None:
            formatted_target = f"{target:.1f}{unit}"
    else:
        formatted_value = f"{value:,}{unit}"
        if previous_value is not None:
            formatted_previous = f"{previous_value:,}{unit}"
        if target is not None:
            formatted_target = f"{target:,}{unit}"
    
    # Calculate change for comparison
    if previous_value is not None and previous_value != 0:
        change = ((value - previous_value) / previous_value) * 100
        change_text = f"{change:+.1f}%"
        
        # Determine color based on direction and desirability
        color = ""
        if change > 0:
            if "taux" in title.lower() or "defaut" in title.lower() or "rebut" in title.lower():
                # Higher is bad for defect rates
                color = "red"
                icon = "↑"
            else:
                # Higher is good for most other metrics
                color = "green" 
                icon = "↑"
        elif change < 0:
            if "taux" in title.lower() or "defaut" in title.lower() or "rebut" in title.lower():
                # Lower is good for defect rates
                color = "green"
                icon = "↓"
            else:
                # Lower is bad for most other metrics
                color = "red"
                icon = "↓"
        else:
            color = "gray"
            icon = "→"
            
        comparison = f'<span style="color: {color};">{icon} {change_text}</span> vs période précédente'
    else:
        comparison = ""
    
    # Target comparison (if provided)
    if target is not None:
        progress = (value / target) * 100 if target != 0 else 0
        progress_width = min(100, progress)
        
        target_bar = f"""
        <div style="width: 100%; background-color: #f3f4f6; height: 4px; border-radius: 2px; margin-top: 8px;">
            <div style="width: {progress_width}%; background-color: #3b82f6; height: 4px; border-radius: 2px;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 12px; color: #9ca3af; margin-top: 4px;">
            <span>0</span>
            <span>Objectif: {formatted_target}</span>
        </div>
        """
    else:
        target_bar = ""
    
    st.markdown(
        f"""
        <div style="background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); height: 100%;">
            <div style="font-size: 14px; color: #64748b; margin-bottom: 8px;">{title}</div>
            <div style="font-size: 28px; font-weight: 700; color: #1e40af; margin-bottom: 5px;">{formatted_value}</div>
            <div style="font-size: 13px; color: #6b7280;">{comparison}</div>
            {target_bar}
        </div>
        """,
        unsafe_allow_html=True
    )

def create_trends_chart(data, date_col, value_col, title="Evolution temporelle", color="#3b82f6"):
    """Create a line chart showing the evolution of a metric over time"""
    # Group by date and calculate mean or sum
    if data.empty:
        # Return empty chart with message
        fig = go.Figure()
        fig.update_layout(
            title=title + " - Aucune donnée disponible",
            xaxis_title="Date",
            yaxis_title="Valeur",
            height=350,
            margin=dict(l=10, r=10, t=50, b=30),
            font=dict(family="Arial", size=12),
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
    
    # Convert to datetime if needed
    if data[date_col].dtype != 'datetime64[ns]':
        try:
            data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
        except:
            # If conversion fails, use the data as is
            pass
    
    # Group by date
    grouped = data.groupby(date_col)[value_col].mean().reset_index()
    grouped = grouped.sort_values(by=date_col)
    
    # Create figure
    fig = px.line(
        grouped, 
        x=date_col, 
        y=value_col,
        title=title,
        labels={date_col: "Date", value_col: "Valeur"},
        line_shape="linear",
        color_discrete_sequence=[color]
    )
    
    # Add markers
    fig.update_traces(mode='lines+markers', marker=dict(size=8))
    
    # Update layout
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=50, b=30),
        font=dict(family="Arial", size=12),
        xaxis=dict(
            tickformat="%d %b %Y",
            tickangle=-45,
            tickmode="auto",
            nticks=10
        ),
        hovermode="x unified"
    )
    
    # Add trend line using moving average
    if len(grouped) > 5:
        grouped['MA'] = grouped[value_col].rolling(window=min(5, len(grouped)), min_periods=1).mean()
        fig.add_scatter(
            x=grouped[date_col],
            y=grouped['MA'],
            mode='lines',
            name='Tendance',
            line=dict(color='rgba(255, 0, 0, 0.5)', width=2, dash='dash')
        )
    
    return fig

def create_pareto_chart(data, category_col, value_col, title="Analyse Pareto", color_palette=None):
    """Create a Pareto chart for defect analysis"""
    if data.empty or category_col not in data.columns:
        # Return empty chart with message
        fig = go.Figure()
        fig.update_layout(
            title=title + " - Aucune donnée disponible",
            height=400,
            margin=dict(l=10, r=10, t=50, b=30),
            font=dict(family="Arial", size=12),
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
    
    # Group by category and sum values
    grouped = data.groupby(category_col)[value_col].sum().reset_index()
    
    # Sort by value descending
    grouped = grouped.sort_values(by=value_col, ascending=False)
    
    # Limit to top 10 categories
    grouped = grouped.head(10)
    
    # Calculate cumulative percentage
    total = grouped[value_col].sum()
    grouped['percent'] = (grouped[value_col] / total * 100)
    grouped['cumulative_percent'] = grouped['percent'].cumsum()
    
    # Create the bar chart
    color_sequence = color_palette or px.colors.qualitative.Set1
    fig = go.Figure()
    
    # Add bars
    fig.add_trace(go.Bar(
        x=grouped[category_col],
        y=grouped[value_col],
        name='Valeur',
        marker_color=color_sequence[0]
    ))
    
    # Add cumulative percentage line
    fig.add_trace(go.Scatter(
        x=grouped[category_col],
        y=grouped['cumulative_percent'],
        name='% Cumulatif',
        yaxis='y2',
        line=dict(color=color_sequence[1], width=3),
        marker=dict(size=10)
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        height=400,
        margin=dict(l=10, r=10, t=50, b=100),
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
        xaxis=dict(
            title="Catégorie",
            tickangle=-45
        ),
        yaxis=dict(
            title="Valeur",
            side="left"
        ),
        yaxis2=dict(
            title="% Cumulatif",
            side="right",
            range=[0, 100],
            overlaying="y",
            ticksuffix="%"
        ),
        hovermode="x unified"
    )
    
    return fig

def create_pie_chart(data, names, values, title="Distribution", color_palette=None):
    """Create a donut chart for distribution analysis"""
    if data.empty or names not in data.columns:
        # Return empty chart with message
        fig = go.Figure()
        fig.update_layout(
            title=title + " - Aucune donnée disponible",
            height=350,
            margin=dict(l=10, r=10, t=50, b=30),
            font=dict(family="Arial", size=12),
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
    
    # Sort by value descending
    grouped = grouped.sort_values(by=values, ascending=False)
    
    # Limit to top 8 categories
    if len(grouped) > 8:
        top_categories = grouped.head(7)
        others = pd.DataFrame({
            names: ["Autres"],
            values: [grouped.iloc[7:][values].sum()]
        })
        grouped = pd.concat([top_categories, others])
    
    # Create the pie chart
    color_seq = color_palette or px.colors.qualitative.Set2
    fig = px.pie(
        grouped, 
        names=names, 
        values=values,
        title=title,
        hole=0.4,
        color_discrete_sequence=color_seq
    )
    
    # Update layout
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=50, b=30),
        font=dict(family="Arial", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    
    # Add total in center
    total = grouped[values].sum()
    fig.add_annotation(
        text=f"Total<br>{total:,.0f}",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color="black", family="Arial, sans-serif")
    )
    
    return fig

def calculate_tactical_metrics(filtered_data):
    """Calculate metrics for the tactical dashboard"""
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
    
    # Find relevant columns using multiple potential names
    categorie_column = get_column(['Categorie', 'categorie', 'CategoryType'])
    type_column = get_column(['Type', 'type', 'TypeControle'])
    defaut_column = get_column(['TypeDefaut', 'typedefaut', 'DefautType', 'CodeDefaut'])
    qtte_column = get_column(['Qtte', 'qtte', 'Quantite', 'NbrReclamations'])
    qttesondee_column = get_column(['QtteSondee', 'qttesondee'])
    temps_column = get_column(['Temps', 'temps', 'TempsRetouche'])
    operation_column = get_column(['Operation', 'operation', 'IDOperation', 'idoperation', 'Libelle'])
    fournisseur_column = get_column(['Fournisseur', 'IDTiers', 'IDTiers1'])
    controleur_column = get_column(['Controleur', 'IDControleur', 'controleur'])
    
    # 1. Total items with issues
    total_items = filtered_data[qtte_column].sum() if qtte_column else filtered_data.shape[0]
    metrics['total_issues'] = total_items
    
    # 2. Defect rate per type
    if qttesondee_column and qtte_column:
        total_inspected = filtered_data[qttesondee_column].sum()
        if total_inspected > 0:
            metrics['defect_rate'] = (total_items / total_inspected) * 100
        else:
            metrics['defect_rate'] = 0
    else:
        # Estimate based on typical rates
        metrics['defect_rate'] = (total_items / (total_items * 5)) * 100
    
    # 3. Average repair time
    if temps_column:
        metrics['avg_repair_time'] = filtered_data[temps_column].mean() if not filtered_data.empty else 0
    else:
        metrics['avg_repair_time'] = 0
    
    # 4. Defects by category
    if categorie_column:
        category_counts = filtered_data.groupby(categorie_column).size().reset_index(name='count')
        metrics['top_category'] = category_counts.iloc[0][categorie_column] if not category_counts.empty else "N/A"
        metrics['top_category_count'] = category_counts.iloc[0]['count'] if not category_counts.empty else 0
    else:
        metrics['top_category'] = "N/A"
        metrics['top_category_count'] = 0
    
    # 5. Defects by operation
    if operation_column:
        operation_counts = filtered_data.groupby(operation_column).size().reset_index(name='count')
        operation_counts = operation_counts.sort_values(by='count', ascending=False)
        metrics['top_operation'] = operation_counts.iloc[0][operation_column] if not operation_counts.empty else "N/A"
        metrics['top_operation_count'] = operation_counts.iloc[0]['count'] if not operation_counts.empty else 0
    else:
        metrics['top_operation'] = "N/A"
        metrics['top_operation_count'] = 0
    
    # 6. Defects by supplier
    if fournisseur_column:
        supplier_counts = filtered_data.groupby(fournisseur_column).size().reset_index(name='count')
        supplier_counts = supplier_counts.sort_values(by='count', ascending=False)
        metrics['top_supplier'] = supplier_counts.iloc[0][fournisseur_column] if not supplier_counts.empty else "N/A"
        metrics['top_supplier_count'] = supplier_counts.iloc[0]['count'] if not supplier_counts.empty else 0
    else:
        metrics['top_supplier'] = "N/A"
        metrics['top_supplier_count'] = 0
    
    # 7. Most common defect type
    if defaut_column:
        defect_counts = filtered_data.groupby(defaut_column).size().reset_index(name='count')
        defect_counts = defect_counts.sort_values(by='count', ascending=False)
        metrics['top_defect'] = defect_counts.iloc[0][defaut_column] if not defect_counts.empty else "N/A"
        metrics['top_defect_count'] = defect_counts.iloc[0]['count'] if not defect_counts.empty else 0
        
        # Calculate defect distribution
        total_defects = defect_counts['count'].sum()
        metrics['defect_distribution'] = defect_counts
        metrics['defect_distribution']['percentage'] = (defect_counts['count'] / total_defects * 100).round(1)
    else:
        metrics['top_defect'] = "N/A"
        metrics['top_defect_count'] = 0
        metrics['defect_distribution'] = pd.DataFrame()
    
    # 8. Controller performance
    if controleur_column and qtte_column:
        controller_performance = filtered_data.groupby(controleur_column)[qtte_column].agg(['sum', 'count']).reset_index()
        controller_performance.columns = [controleur_column, 'issues_found', 'inspections']
        controller_performance = controller_performance.sort_values(by='issues_found', ascending=False)
        metrics['controller_performance'] = controller_performance
        
        # Get top controller
        metrics['top_controller'] = controller_performance.iloc[0][controleur_column] if not controller_performance.empty else "N/A"
        metrics['top_controller_count'] = controller_performance.iloc[0]['issues_found'] if not controller_performance.empty else 0
    else:
        metrics['controller_performance'] = pd.DataFrame()
        metrics['top_controller'] = "N/A"
        metrics['top_controller_count'] = 0
    
    return metrics

def create_tactical_dashboard(data):
    """Create a complete tactical dashboard with metrics and visualizations"""
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
    .metric-container {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Dashboard Title
    st.markdown("<div class='dashboard-title'>📈 Dashboard Tactique</div>", unsafe_allow_html=True)
    
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
            # Category Filter
            category_cols = [col for col in data.columns if col.lower() in ['categorie', 'categorytype']]
            if category_cols:
                category_col = category_cols[0]
                category_options = ["Tous"] + sorted([str(x) for x in data[category_col].dropna().unique() if str(x).strip()])
                selected_category = st.selectbox("Catégorie:", category_options)
            else:
                st.warning("Colonne de catégorie non trouvée")
                selected_category = "Tous"
    
    # Add more filters in an expander
    with st.expander("Filtres avancés"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Defect Type Filter
            defect_cols = [col for col in data.columns if col.lower() in ['typedefaut', 'defauttype', 'codedefaut']]
            if defect_cols:
                defect_col = defect_cols[0]
                defect_options = ["Tous"] + sorted([str(x) for x in data[defect_col].dropna().unique() if str(x).strip()])
                selected_defect = st.selectbox("Type de défaut:", defect_options)
            else:
                st.warning("Colonne de type de défaut non trouvée")
                selected_defect = "Tous"
        
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
    
    # Apply category filter
    if category_cols and selected_category != "Tous":
        category_col = category_cols[0]
        filtered_data = apply_categorical_filter(filtered_data, category_col, [selected_category])
    
    # Apply defect type filter
    if defect_cols and selected_defect != "Tous":
        defect_col = defect_cols[0]
        filtered_data = apply_categorical_filter(filtered_data, defect_col, [selected_defect])
    
    # Apply controller filter
    if controller_cols and selected_controller != "Tous":
        controller_col = controller_cols[0]
        filtered_data = apply_categorical_filter(filtered_data, controller_col, [selected_controller])
    
    # Check if the filtered data is empty
    if filtered_data.empty:
        st.warning("Aucune donnée ne correspond aux filtres sélectionnés. Veuillez ajuster vos filtres.")
        return
    
    # Calculate metrics for filtered data
    metrics = calculate_tactical_metrics(filtered_data)
    
    # KPI Section
    st.markdown("<div class='section-title'>📊 Indicateurs clés de performance</div>", unsafe_allow_html=True)
    
    # Create KPI cards row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_kpi_card("Nombre total de défauts", metrics['total_issues'], unit="")
    
    with col2:
        create_kpi_card("Taux de défauts", metrics['defect_rate'], target=10, unit="%", is_percentage=True)
    
    with col3:
        create_kpi_card("Temps moyen de retouche", metrics['avg_repair_time'], unit=" min")
    
    with col4:
        create_kpi_card("Défaut principal", metrics['top_defect_count'], unit="", is_percentage=False)
    
    # Trends Section
    st.markdown("<div class='section-title'>📈 Analyse des tendances</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create trend chart for defects over time
        date_col = next((col for col in filtered_data.columns if col.lower() in ['date', 'datetime']), None)
        qtte_col = next((col for col in filtered_data.columns if col.lower() in ['qtte', 'quantite', 'nbrreclamations']), None)
        
        if date_col and qtte_col:
            trend_chart = create_trends_chart(
                filtered_data,
                date_col,
                qtte_col,
                title="Évolution des défauts dans le temps",
                color="#3b82f6"
            )
            st.plotly_chart(trend_chart, use_container_width=True)
        else:
            st.info("Données insuffisantes pour afficher l'évolution des défauts")
    
    with col2:
        # Create Pareto chart for defect types
        defect_col = next((col for col in filtered_data.columns if col.lower() in ['typedefaut', 'defauttype', 'codedefaut']), None)
        qtte_col = next((col for col in filtered_data.columns if col.lower() in ['qtte', 'quantite', 'nbrreclamations']), None)
        
        if defect_col and qtte_col:
            pareto_chart = create_pareto_chart(
                filtered_data,
                defect_col,
                qtte_col,
                title="Analyse Pareto des types de défauts",
                color_palette=["#3b82f6", "#ef4444"]
            )
            st.plotly_chart(pareto_chart, use_container_width=True)
        else:
            st.info("Données insuffisantes pour afficher l'analyse Pareto")
    
    # Detailed Analysis Section
    st.markdown("<div class='section-title'>🔍 Analyse détaillée</div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Par opération", "Par fournisseur", "Par contrôleur"])
    
    # TAB 1: Analysis by Operation
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart for operations
            operation_col = next((col for col in filtered_data.columns if col.lower() in ['operation', 'idoperation', 'libelle']), None)
            qtte_col = next((col for col in filtered_data.columns if col.lower() in ['qtte', 'quantite', 'nbrreclamations']), None)
            
            if operation_col and qtte_col:
                pie_chart = create_pie_chart(
                    filtered_data,
                    operation_col,
                    qtte_col,
                    title="Distribution des défauts par opération",
                    color_palette=px.colors.qualitative.Pastel
                )
                st.plotly_chart(pie_chart, use_container_width=True)
            else:
                st.info("Données insuffisantes pour afficher la distribution par opération")
        
        with col2:
            # Top 5 operations table
            if operation_col and qtte_col:
                st.markdown("### Top 5 opérations avec le plus de défauts")
                
                # Group by operation and count defects
                top_operations = filtered_data.groupby(operation_col)[qtte_col].sum().reset_index()
                top_operations = top_operations.sort_values(by=qtte_col, ascending=False).head(5)
                
                # Calculate percentages
                total = top_operations[qtte_col].sum()
                top_operations['pourcentage'] = (top_operations[qtte_col] / total * 100).round(1)
                
                # Rename columns for display
                top_operations.columns = ['Opération', 'Nombre de défauts', '% du total']
                
                # Style the dataframe
                st.dataframe(
                    top_operations,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Données insuffisantes pour afficher le top 5 des opérations")
    
    # TAB 2: Analysis by Supplier
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart for suppliers
            supplier_col = next((col for col in filtered_data.columns if col.lower() in ['fournisseur', 'idtiers', 'idtiers1']), None)
            qtte_col = next((col for col in filtered_data.columns if col.lower() in ['qtte', 'quantite', 'nbrreclamations']), None)
            
            if supplier_col and qtte_col:
                pie_chart = create_pie_chart(
                    filtered_data,
                    supplier_col,
                    qtte_col,
                    title="Distribution des défauts par fournisseur",
                    color_palette=px.colors.qualitative.Set3
                )
                st.plotly_chart(pie_chart, use_container_width=True)
            else:
                st.info("Données insuffisantes pour afficher la distribution par fournisseur")
        
        with col2:
            # Top 5 suppliers table
            if supplier_col and qtte_col:
                st.markdown("### Top 5 fournisseurs avec le plus de défauts")
                
                # Group by supplier and count defects
                top_suppliers = filtered_data.groupby(supplier_col)[qtte_col].sum().reset_index()
                top_suppliers = top_suppliers.sort_values(by=qtte_col, ascending=False).head(5)
                
                # Calculate percentages
                total = top_suppliers[qtte_col].sum()
                top_suppliers['pourcentage'] = (top_suppliers[qtte_col] / total * 100).round(1)
                
                # Rename columns for display
                top_suppliers.columns = ['Fournisseur', 'Nombre de défauts', '% du total']
                
                # Style the dataframe
                st.dataframe(
                    top_suppliers,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Données insuffisantes pour afficher le top 5 des fournisseurs")
    
    # TAB 3: Analysis by Controller
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart for controllers
            controller_col = next((col for col in filtered_data.columns if col.lower() in ['controleur', 'idcontroleur']), None)
            qtte_col = next((col for col in filtered_data.columns if col.lower() in ['qtte', 'quantite', 'nbrreclamations']), None)
            
            if controller_col and qtte_col:
                pie_chart = create_pie_chart(
                    filtered_data,
                    controller_col,
                    qtte_col,
                    title="Distribution des défauts par contrôleur",
                    color_palette=px.colors.qualitative.Pastel1
                )
                st.plotly_chart(pie_chart, use_container_width=True)
            else:
                st.info("Données insuffisantes pour afficher la distribution par contrôleur")
        
        with col2:
            # Top 5 controllers table
            if controller_col and qtte_col:
                st.markdown("### Top 5 contrôleurs avec le plus de défauts détectés")
                
                # Group by controller and count defects
                top_controllers = filtered_data.groupby(controller_col)[qtte_col].sum().reset_index()
                top_controllers = top_controllers.sort_values(by=qtte_col, ascending=False).head(5)
                
                # Calculate percentages
                total = top_controllers[qtte_col].sum()
                top_controllers['pourcentage'] = (top_controllers[qtte_col] / total * 100).round(1)
                
                # Rename columns for display
                top_controllers.columns = ['Contrôleur', 'Nombre de défauts', '% du total']
                
                # Style the dataframe
                st.dataframe(
                    top_controllers,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Données insuffisantes pour afficher le top 5 des contrôleurs")
    
    # Quality Distribution by Type Section
    st.markdown("<div class='section-title'>📊 Distribution des défauts par type</div>", unsafe_allow_html=True)
    
    defect_col = next((col for col in filtered_data.columns if col.lower() in ['typedefaut', 'defauttype', 'codedefaut']), None)
    
    if defect_col:
        # Count defects by type
        defect_counts = filtered_data.groupby(defect_col).size().reset_index(name='count')
        defect_counts = defect_counts.sort_values(by='count', ascending=False)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Create horizontal bar chart for defect types
            if not defect_counts.empty:
                fig = px.bar(
                    defect_counts.head(10),
                    y=defect_col,
                    x='count',
                    orientation='h',
                    title="Top 10 types de défauts",
                    labels={defect_col: "Type de défaut", 'count': "Nombre de défauts"},
                    color='count',
                    color_continuous_scale=px.colors.sequential.Blues
                )
                
                fig.update_layout(
                    height=400,
                    margin=dict(l=10, r=10, t=50, b=30),
                    yaxis={'categoryorder': 'total ascending'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnée de type de défaut disponible")
        
        with col2:
            # Display defect statistics
            st.markdown("### Statistiques des défauts")
            
            if not defect_counts.empty:
                # Calculate percentages
                total = defect_counts['count'].sum()
                defect_counts['pourcentage'] = (defect_counts['count'] / total * 100).round(1)
                
                # Summary metrics
                total_defect_types = len(defect_counts)
                top_3_percentage = defect_counts.head(3)['pourcentage'].sum()
                
                st.markdown(f"""
                <div class="metric-container">
                    <p><strong>Nombre total de types de défauts:</strong> {total_defect_types}</p>
                    <p><strong>Top 3 des défauts représentent:</strong> {top_3_percentage:.1f}% du total</p>
                    <p><strong>Défaut le plus fréquent:</strong> {defect_counts.iloc[0][defect_col]} ({defect_counts.iloc[0]['pourcentage']:.1f}%)</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Add a quick summary of recommendations
                st.markdown("### Recommandations")
                st.markdown("""
                <div class="metric-container">
                    <p>📌 Concentrez vos efforts sur les 3 principaux types de défauts pour un impact maximal</p>
                    <p>📌 Analysez les causes racines des défauts les plus fréquents</p>
                    <p>📌 Établissez un plan d'action pour réduire les défauts par type</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Aucune statistique de défaut disponible")
    else:
        st.info("Données de type de défaut non disponibles")
    
    # Footer
    st.markdown("""
    <div style="margin-top: 40px; padding: 15px; text-align: center; color: #64748b; border-top: 1px solid #e2e8f0;">
        <p>Dashboard Tactique v2.0 - Dernière mise à jour: Mars 2025</p>
    </div>
    """, unsafe_allow_html=True)