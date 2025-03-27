import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, apply_all_filters, create_gauge_chart

# Create tactical dashboard header
def create_tactical_header():
    st.markdown("""
    <div style="background-color:#5c6bc0; padding:10px; border-radius:10px">
        <h1 style="color:white; text-align:center">Dashboard Tactique</h1>
        <h3 style="color:white; text-align:center">Niveau chefs services</h3>
    </div>
    """, unsafe_allow_html=True)

# Create tactical metrics
def create_tactical_metrics(filtered_data):
    # Calculate metrics for Retouche section
    retouche_count = filtered_data['Retouche'].sum() if 'Retouche' in filtered_data.columns else 0
    retouche_rate = (filtered_data['Retouche_Count'].sum() / filtered_data['Quantite'].sum() * 100) if all(col in filtered_data.columns for col in ['Retouche_Count', 'Quantite']) else 0
    retouche_time = filtered_data['Temps_Retouche'].sum() if 'Temps_Retouche' in filtered_data.columns else 0
    retouche_time_rate = (retouche_time / (filtered_data['Quantite'] * filtered_data['Temps_Gamme']).sum() * 100) if all(col in filtered_data.columns for col in ['Temps_Retouche', 'Quantite', 'Temps_Gamme']) else 0
    retouche_cost = filtered_data['Retouche'].sum() if 'Retouche' in filtered_data.columns else 0
    retouche_cost_rate = (retouche_cost / (filtered_data['Quantite'] * filtered_data['Prix_Vente']).sum() * 100) if all(col in filtered_data.columns for col in ['Retouche', 'Quantite', 'Prix_Vente']) else 0
    
    # Calculate metrics for Rebut section
    rebut_count = filtered_data['Rebut'].sum() if 'Rebut' in filtered_data.columns else 0
    rebut_rate = (filtered_data['Rebut_Count'].sum() / filtered_data['Quantite_Coupee'].sum() * 100) if all(col in filtered_data.columns for col in ['Rebut_Count', 'Quantite_Coupee']) else 0
    rebut_cost = filtered_data['Rebut'].sum() if 'Rebut' in filtered_data.columns else 0
    rebut_cost_rate = (rebut_cost / (filtered_data['Quantite_Exportee'] * filtered_data['Prix_Unitaire']).sum() * 100) if all(col in filtered_data.columns for col in ['Rebut', 'Quantite_Exportee', 'Prix_Unitaire']) else 0
    
    # Calculate metrics for Penalite section
    penalite = filtered_data['Penalite'].sum() if 'Penalite' in filtered_data.columns else 0
    penalite_rate = (penalite / (filtered_data['Quantite_Exportee'] * filtered_data['Prix_Unitaire']).sum() * 100) if all(col in filtered_data.columns for col in ['Penalite', 'Quantite_Exportee', 'Prix_Unitaire']) else 0
    
    # Return all calculated metrics
    return {
        "retouche_count": retouche_count,
        "retouche_rate": retouche_rate,
        "retouche_time": retouche_time,
        "retouche_time_rate": retouche_time_rate,
        "retouche_cost": retouche_cost,
        "retouche_cost_rate": retouche_cost_rate,
        "rebut_count": rebut_count,
        "rebut_rate": rebut_rate,
        "rebut_cost": rebut_cost,
        "rebut_cost_rate": rebut_cost_rate,
        "penalite": penalite,
        "penalite_rate": penalite_rate
    }

# Create top defects pie chart
def create_top_defects_pie(filtered_data, category, n=3, title=None):
    if f'{category}_Defaut' not in filtered_data.columns:
        # Fallback to sample data if column doesn't exist
        return px.pie(
            names=["No Data Available"],
            values=[1],
            title=title or f"Répartition Top {n} défauts",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
    
    # Group by defect and sum the category value
    defect_data = filtered_data.groupby(f'{category}_Defaut')[category].sum().reset_index()
    defect_data = defect_data.sort_values(category, ascending=False).head(n)
    
    # Get top N defects
    top_defects = defect_data[f'{category}_Defaut'].tolist()
    other_sum = filtered_data[~filtered_data[f'{category}_Defaut'].isin(top_defects)][category].sum()
    
    # Add "Other" category if there are more defects
    if other_sum > 0:
        defect_data = pd.concat([
            defect_data,
            pd.DataFrame({f'{category}_Defaut': ['Autres'], category: [other_sum]})
        ])
    
    # Create pie chart
    fig = px.pie(
        defect_data,
        names=f'{category}_Defaut',
        values=category,
        title=title or f"Répartition Top {n} défauts",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    # Update layout
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=30, b=10),
        height=250,
        font=dict(size=10)
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

# Create top providers pie chart
def create_top_providers_pie(filtered_data, category, n=3, title=None):
    if f'{category}_Prestataire' not in filtered_data.columns:
        # Fallback to sample data if column doesn't exist
        return px.pie(
            names=["No Data Available"],
            values=[1],
            title=title or f"Répartition Top {n} prestataires",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
    
    # Group by provider and sum the category value
    provider_data = filtered_data.groupby(f'{category}_Prestataire')[category].sum().reset_index()
    provider_data = provider_data.sort_values(category, ascending=False).head(n)
    
    # Get top N providers
    top_providers = provider_data[f'{category}_Prestataire'].tolist()
    other_sum = filtered_data[~filtered_data[f'{category}_Prestataire'].isin(top_providers)][category].sum()
    
    # Add "Other" category if there are more providers
    if other_sum > 0:
        provider_data = pd.concat([
            provider_data,
            pd.DataFrame({f'{category}_Prestataire': ['Autres'], category: [other_sum]})
        ])
    
    # Create pie chart
    fig = px.pie(
        provider_data,
        names=f'{category}_Prestataire',
        values=category,
        title=title or f"Répartition Top {n} prestataires",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    # Update layout
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=30, b=10),
        height=250,
        font=dict(size=10)
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

# Create historical trend line chart
def create_trend_chart(filtered_data, category, group_by, title=None):
    if category not in filtered_data.columns or 'DATE' not in filtered_data.columns:
        # Fallback to empty chart if columns don't exist
        fig = go.Figure()
        fig.update_layout(
            title=title or f"Historique {category}",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=30, b=10),
            height=200,
            font=dict(size=10)
        )
        fig.add_annotation(
            text="No data available",
            showarrow=False,
            font=dict(size=14)
        )
        return fig
    
    # Convert date to monthly format
    filtered_data['Month'] = pd.to_datetime(filtered_data['DATE']).dt.strftime('%Y-%m')
    
    # Check if group_by exists in the dataframe
    if group_by and group_by in filtered_data.columns:
        # Group by month and the specified group_by column
        trend_data = filtered_data.groupby(['Month', group_by])[category].sum().reset_index()
        
        # Create line chart
        fig = px.line(
            trend_data,
            x='Month',
            y=category,
            color=group_by,
            title=title or f"Historique {category} par {group_by}",
            markers=True
        )
    else:
        # Group by month only
        trend_data = filtered_data.groupby('Month')[category].sum().reset_index()
        
        # Create line chart
        fig = px.line(
            trend_data,
            x='Month',
            y=category,
            title=title or f"Historique {category}",
            markers=True
        )
    
    # Add moving average
    window_size = 3 if len(trend_data['Month'].unique()) >= 3 else len(trend_data['Month'].unique())
    if window_size > 0 and not group_by:
        # Calculate moving average
        trend_data['MA'] = trend_data[category].rolling(window=window_size, min_periods=1).mean()
        
        # Add moving average line
        fig.add_scatter(
            x=trend_data['Month'],
            y=trend_data['MA'],
            mode='lines',
            name=f'Moyenne mobile sur {window_size}',
            line=dict(color='black', width=2, dash='dot')
        )
    
    # Update layout
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=30, b=10),
        height=200,
        font=dict(size=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

# Create tactical dashboard layout
def create_tactical_dashboard(data):
    # Create header
    create_tactical_header()
    
    # Create filters
    st.markdown("### Filtres")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Date range filter
        start_date = st.date_input("Date de début", 
                                   value=pd.to_datetime(data['DATE'].min()) if 'DATE' in data.columns else None)
        end_date = st.date_input("Date de fin", 
                                value=pd.to_datetime(data['DATE'].max()) if 'DATE' in data.columns else None)
    
    with col2:
        # KWM filter
        kwm_options = sorted(data['KWM'].unique().tolist()) if 'KWM' in data.columns else []
        selected_kwm = st.multiselect("KWM", options=kwm_options)
    
    with col3:
        # Client filter
        client_options = sorted(data['Client'].unique().tolist()) if 'Client' in data.columns else []
        selected_client = st.multiselect("Client", options=client_options)
    
    with col4:
        # Prestataire filter
        provider_options = sorted(data['Prestataire'].unique().tolist()) if 'Prestataire' in data.columns else []
        selected_provider = st.multiselect("Prestataire", options=provider_options)
    
    # Build filters dictionary
    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "kwm": selected_kwm,
        "client": selected_client,
        "provider": selected_provider
    }
    
    # Apply filters
    filtered_data = apply_all_filters(data, filters)
    
    # Calculate metrics
    metrics = create_tactical_metrics(filtered_data)
    
    # Create dashboard layout
    st.markdown("## Tableau de bord tactique")
    
    # ---------------- RETOUCHE SECTION ----------------
    st.markdown("### Retouche")
    row1_cols = st.columns([1, 1, 1, 1])
    
    # Top defects for Retouche
    with row1_cols[0]:
        defects_pie = create_top_defects_pie(filtered_data, 'Retouche', n=3, title="Répartition Top 3 défauts")
        st.plotly_chart(defects_pie, use_container_width=True)
    
    # Cost gauge for Retouche
    with row1_cols[1]:
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
            title="Coût Retouche Cumulé"
        )
        st.plotly_chart(retouche_gauge, use_container_width=True)
    
    # Top providers for Retouche
    with row1_cols[2]:
        providers_pie = create_top_providers_pie(filtered_data, 'Retouche', n=3, title="Répartition Top 3 prestataires")
        st.plotly_chart(providers_pie, use_container_width=True)
    
    # Retouche metrics
    with row1_cols[3]:
        st.markdown("#### Métriques Retouche")
        col1, col2 = st.columns(2)
        col1.metric("Nombre de retouche", f"{metrics['retouche_count']:,.0f} pcs")
        col2.metric("Taux de retouche", f"{metrics['retouche_rate']:.2f}%")
        col1.metric("Temps de retouche", f"{metrics['retouche_time']:,.0f} min")
        col2.metric("Taux temps retouche", f"{metrics['retouche_time_rate']:.2f}%")
        col1.metric("Coût de retouche", f"{metrics['retouche_cost']:,.0f} TND")
        col2.metric("% coût de retouche", f"{metrics['retouche_cost_rate']:.2f}%")
    
    # Line charts for Retouche
    row2_cols = st.columns(2)
    
    with row2_cols[0]:
        defect_trend = create_trend_chart(
            filtered_data, 
            'Retouche', 
            'Retouche_Defaut', 
            title="Historique Top 3 Défauts"
        )
        st.plotly_chart(defect_trend, use_container_width=True)
    
    with row2_cols[1]:
        provider_trend = create_trend_chart(
            filtered_data, 
            'Retouche', 
            'Retouche_Prestataire', 
            title="Historique Top 3 prestataires"
        )
        st.plotly_chart(provider_trend, use_container_width=True)
    
    # ---------------- REBUT SECTION ----------------
    st.markdown("### Rebut")
    row3_cols = st.columns([1, 1, 1, 1])
    
    # Top defects for Rebut
    with row3_cols[0]:
        defects_pie = create_top_defects_pie(filtered_data, 'Rebut', n=3, title="Répartition Top 3 défauts")
        st.plotly_chart(defects_pie, use_container_width=True)
    
    # Cost gauge for Rebut
    with row3_cols[1]:
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
            title="Coût Rebut Cumulé"
        )
        st.plotly_chart(rebut_gauge, use_container_width=True)
    
    # Top providers for Rebut
    with row3_cols[2]:
        providers_pie = create_top_providers_pie(filtered_data, 'Rebut', n=3, title="Répartition Top 3 prestataires")
        st.plotly_chart(providers_pie, use_container_width=True)
    
    # Rebut metrics
    with row3_cols[3]:
        st.markdown("#### Métriques Rebut")
        col1, col2 = st.columns(2)
        col1.metric("Rebut", f"{metrics['rebut_count']:,.0f} pcs")
        col2.metric("Taux rebut", f"{metrics['rebut_rate']:.2f}%")
        col1.metric("Coût rebut", f"{metrics['rebut_cost']:,.0f} TND")
        col2.metric("Taux coût de rebut", f"{metrics['rebut_cost_rate']:.2f}%")
    
    # Line charts for Rebut
    row4_cols = st.columns(2)
    
    with row4_cols[0]:
        defect_trend = create_trend_chart(
            filtered_data, 
            'Rebut', 
            'Rebut_Defaut', 
            title="Historique Top 3 Défauts"
        )
        st.plotly_chart(defect_trend, use_container_width=True)
    
    with row4_cols[1]:
        provider_trend = create_trend_chart(
            filtered_data, 
            'Rebut', 
            'Rebut_Prestataire', 
            title="Historique Top 3 prestataires"
        )
        st.plotly_chart(provider_trend, use_container_width=True)
    
    # ---------------- PENALITE SECTION ----------------
    st.markdown("### Pénalité")
    row5_cols = st.columns([1, 1, 1, 1])
    
    # Penalty metrics
    with row5_cols[0]:
        st.markdown("#### Métriques Pénalité")
        col1, col2 = st.columns(2)
        col1.metric("Pénalité qualité", f"{metrics['penalite']:,.0f} TND")
        col2.metric("Taux Pénalité qualité", f"{metrics['penalite_rate']:.2f}%")
    
    # Cost gauge for Penalty
    with row5_cols[1]:
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
            title="Pénalités Cumulées"
        )
        st.plotly_chart(penalty_gauge, use_container_width=True)
    
    # Defects and distribution for Penalty
    with row5_cols[2]:
        defects_pie = create_top_defects_pie(filtered_data, 'Penalite', n=3, title="Répartition Pénalités")
        st.plotly_chart(defects_pie, use_container_width=True)
    
    with row5_cols[3]:
        penalty_trend = create_trend_chart(
            filtered_data, 
            'Penalite', 
            None, 
            title="Historique Pénalités"
        )
        st.plotly_chart(penalty_trend, use_container_width=True)