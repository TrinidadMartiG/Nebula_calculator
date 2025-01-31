import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def clear_inputs():
    # Reset all input values to 0
    st.session_state['ke'] = 0.0
    st.session_state['dosis'] = 0.0
    st.session_state['intervalo'] = 0.0
    st.session_state['vd'] = 0.0

st.title("Dosis múltiple vía endovenosa 💉")

def calculate_ke(cl, vd):
    """Calculate elimination constant (Ke)"""
    try:
        if vd == 0:
            return 0
        return round(cl/vd, 3)
    except:
        return 0

def calculate_half_life(ke):
    """Calculate half life"""
    try:
        if ke == 0:
            return 0
        return round(0.693/ke, 2)
    except:
        return 0

def calculate_cp_values(dosis, vd, ke, intervalo, num_doses=5, points_per_interval=10):
    """Calculate concentration values over time"""
    total_time = intervalo * num_doses
    t = np.linspace(0, total_time, num_doses * points_per_interval)
    cp = np.zeros_like(t)
    
    for dose in range(num_doses):
        dose_time = dose * intervalo
        mask = t >= dose_time
        cp[mask] += (dosis/vd) * np.exp(-ke * (t[mask] - dose_time))
    
    return t, cp

# Layout with two columns
col1, col_gap, col2 = st.columns([1.5, 1, 1.5])

with col1:
    ke = st.number_input("Ke (h⁻¹)", min_value=0.0, format="%.3f", key='ke')
    dosis = st.number_input("Dosis (mg)", min_value=0.0, format="%.1f", key='dosis')
    
with col2:
    intervalo = st.number_input("Intervalo (h)", min_value=0.0, format="%.1f", key='intervalo')
    vd = st.number_input("Volumen de distribución (L)", min_value=0.0, format="%.1f", key='vd')

# Calculate and display results
st.write("")
with st.container():
    col_title, col_button = st.columns([4, 1])
    with col_title:
        st.header("Resultados 🧾")
    with col_button:
        st.write("")
        st.button("Limpiar valores", on_click=clear_inputs, type="primary")

# Results section
if all(v != 0 for v in [ke, dosis, intervalo, vd]):
    # Calculate values
    t12 = calculate_half_life(ke)
    
    # Calculate Cmin and Cmax for first dose
    cmax_first = dosis/vd
    cmin_first = cmax_first * math.exp(-ke * intervalo)
    
    # Calculate steady state concentrations
    factor = 1/(1 - math.exp(-ke * intervalo))
    cmax_ss = cmax_first * factor
    cmin_ss = cmin_first * factor
    
    col3, col_gap2, col4 = st.columns([1.5, 1, 1.5])
    
    with col3:
        st.markdown(f"Cmín primera dosis: :green-background[**{cmin_first:.2f} mg/L**]")
        st.markdown(f"Cmáx primera dosis: :green-background[**{cmax_first:.2f} mg/L**]")
        st.markdown(f"Vida media (t½): :green-background[**{t12} h**]")

    with col4:
        st.markdown(f"Cmín estado estable: :green-background[**{cmin_ss:.2f} mg/L**]")
        st.markdown(f"Cmáx estado estable: :green-background[**{cmax_ss:.2f} mg/L**]")
        st.markdown(f"Tiempo estado estable: :green-background[**{round(5*t12, 2)} h**]")
    
    # Generate concentration-time plot
    st.write("")
    st.subheader("Gráfica concentración-tiempo 📈")
    
    # Generate data points
    t, cp = calculate_cp_values(dosis, vd, ke, intervalo)
    
    # Create the interactive plot using Plotly
    fig = go.Figure()
    
    # Add concentration line
    fig.add_trace(go.Scatter(
        x=t,
        y=cp,
        name='Concentración plasmática',
        line=dict(color='blue'),
        hovertemplate='Tiempo: %{x:.1f}h<br>Concentración: %{y:.2f}mg/L<extra></extra>'
    ))
    
    # Add steady state lines
    fig.add_trace(go.Scatter(
        x=[t[0], t[-1]],
        y=[cmax_ss, cmax_ss],
        name='Cmáx estado estable',
        line=dict(color='red', dash='dash'),
        hovertemplate='Cmáx SS: %{y:.2f}mg/L<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[t[0], t[-1]],
        y=[cmin_ss, cmin_ss],
        name='Cmín estado estable',
        line=dict(color='red', dash='dash'),
        hovertemplate='Cmín SS: %{y:.2f}mg/L<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        xaxis_title="Tiempo (h)",
        yaxis_title="Concentración (mg/L)",
        hovermode='x unified',
        plot_bgcolor='white',
        width=800,
        height=500
    )
    
    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ Por favor, ingrese todos los valores para ver los resultados.") 