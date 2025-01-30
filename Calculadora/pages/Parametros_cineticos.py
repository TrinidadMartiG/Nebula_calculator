import streamlit as st
import math

def clear_inputs():
    # Reset all input values to 0
    st.session_state['peso'] = 0.0
    st.session_state['talla'] = 0
    st.session_state['dosis'] = 0
    st.session_state['intervalo'] = 0
    st.session_state['conc_peak'] = 0.0
    st.session_state['conc_basal'] = 0.0
    st.session_state['t_infusion'] = 0.0
    st.session_state['t_ini_dosis'] = 0.0
    st.session_state['t_ini_dosis_2'] = 0.0

# Título de la aplicación
st.title("Parámetros cinéticos 📈📉")

# Funciones

def get_dosis_dia(dosis, intervalo, peso):
    """Dosis diaria mg/kg/día"""
    try:
        if intervalo == 0 or peso == 0:
            return 0
        formula = (dosis * (24 / intervalo)) / peso
        return round(formula, 2)
    except Exception:
        return 0

# Columnas para organizar la entrada de datos
col1, col_gap, col2 = st.columns([1.5, 1, 1.5])

with col1:
    peso = st.number_input("Peso (kg)", min_value=0.0, format="%.1f", key='peso')
    st.divider()
    dosis = st.number_input("Dosis (mg)", min_value=0, format="%d", key='dosis')
    intervalo = st.number_input("Intervalo entre dosis (hrs)", min_value=0, format="%d", key='intervalo')
    st.divider()
    conc_peak = st.number_input("Concentración 1 (Peak) mcg/mL ", min_value=0.0, format="%.1f", key='conc_peak')
    conc_basal = st.number_input("Concentración 2 (Basal) mcg/mL", min_value=0.0, format="%.1f", key='conc_basal')

with col2:
    talla = st.number_input("Talla (cm)", min_value=0, format="%d", key='talla')
    st.divider()
    t_infusion = st.number_input("Tiempo de infusión (hrs)", min_value=0.0, format="%.1f", key='t_infusion')        
    
    # Add validation before calculating dosis_kg_dia
    if intervalo != 0 and peso != 0:
        dosis_kg_dia = get_dosis_dia(dosis, intervalo, peso)
        st.write(f"Dosis(mg/kg/día): :green-background[**{dosis_kg_dia}**]")
    else:
        st.write("Dosis(mg/kg/día): :red[**0**]")
    st.write(" ")
    st.divider()
    t_ini_dosis = st.number_input("Tiempo 1 (Peak - hrs)", min_value=0.0, format="%.1f", key='t_ini_dosis')
    t_ini_dosis_2 = st.number_input("Tiempo 2 (Basal - hrs)", min_value=0.0, format="%.1f", key='t_ini_dosis_2')

def validate_inputs():
    if (intervalo == 0 or peso == 0 or 
        t_ini_dosis_2 == t_ini_dosis or 
        conc_basal == 0):
        st.error("⚠️ Por favor, revise los valores ingresados. No pueden ser cero: Intervalo, Peso, Tiempo basal-peak. La concentración basal no puede ser cero.")
        return False
    return True

def get_const_eliminacion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2):
    """Constante de eliminación"""
    try:
        if t_ini_dosis_2 == t_ini_dosis or conc_basal == 0:
            return 0
        formula = math.log(conc_peak / conc_basal) / (t_ini_dosis_2 - t_ini_dosis)
        return round(formula, 3)
    except Exception:
        return 0

def get_concentracion_maxima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, t_infusion):
    """Concentración máxima real"""
    try:
        const_eliminacion = get_const_eliminacion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2)
        if const_eliminacion == 0:
            return 0
        formula = conc_peak / math.exp(-const_eliminacion * (t_ini_dosis - t_infusion))
        return round(formula, 2)
    except Exception:
        return 0

def get_concentracion_minima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, intervalo, t_infusion):
    """Concentración mínima real"""
    try:
        conc_max_real = get_concentracion_maxima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, t_infusion)
        const_eliminacion = get_const_eliminacion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2)
        if const_eliminacion == 0:
            return 0
        formula = conc_max_real * math.exp(-const_eliminacion * (intervalo - t_infusion))
        return round(formula, 1)
    except Exception:
        return 0

def get_aclaramiento_medicamento(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, dosis, t_infusion, intervalo):
    """Aclaramiento del medicamento"""
    try:
        vol_distribucion = get_volumen_distribucion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, dosis, t_infusion, intervalo)
        const_eliminacion = get_const_eliminacion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2)
        if const_eliminacion == 0:
            return 0
        formula = (vol_distribucion * const_eliminacion) * 1000 / 60
        return round(formula, 2)
    except Exception:
        return 0

def get_volumen_distribucion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, dosis, t_infusion, intervalo):
    """Volumen de distribución"""
    try:
        const_eliminacion = get_const_eliminacion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2)
        conc_max_real = get_concentracion_maxima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, t_infusion)
        conc_min_real = get_concentracion_minima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, intervalo, t_infusion)
        
        # Validate inputs
        if (t_infusion == 0 or const_eliminacion == 0 or 
            (conc_max_real - conc_min_real * math.exp(-const_eliminacion * t_infusion)) == 0):
            return 0
            
        formula = (dosis * (1 - math.exp(-const_eliminacion * t_infusion))) / (t_infusion * const_eliminacion * (conc_max_real - conc_min_real * math.exp(-const_eliminacion * t_infusion)))
        return round(formula, 2)
    except Exception:
        return 0

def get_area_under_curve(t_infusion, conc_peak, conc_basal, const_eliminacion, intervalo):
    """Área bajo la curva"""
    try:
        if intervalo == 0 or const_eliminacion == 0:
            return 0
        formula = ((t_infusion * ((conc_peak + conc_basal)/2)) + ((conc_peak - conc_basal)/const_eliminacion)) * (24/intervalo)
        return round(formula, 2)
    except Exception:
        return 0

# Mostrar resultados en la columna inferior
st.write(" ")

with st.container():
    col_title, col_button = st.columns([4, 1])
    with col_title:
        st.header("Resultados 🧾✍🏼")
    with col_button:
        st.write(" ")
        st.button("Limpiar valores", on_click=clear_inputs, type="primary")
        
col3, col_gap2, col4 = st.columns([1.5, 1, 2.5])

with col3:
    
    # Cálculo y visualización de la constante de eliminación
    const_eliminacion = get_const_eliminacion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2)
    st.markdown(f"Constante de eliminación: :green-background[**{const_eliminacion} h-1**]")

    conc_max_real = get_concentracion_maxima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, t_infusion)
    st.markdown(f"Concentración máxima real: :green-background[**{conc_max_real} mcg/mL**]")
    
    # Cálculo y visualización de la concentración mínima real
    conc_min_real = get_concentracion_minima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, intervalo, t_infusion)
    st.markdown(f"Concentración mínima real: :green-background[**{conc_min_real} mcg/mL**]")
    
# And in your results section, add validation before displaying:
with col4:
    if validate_inputs():  # Make sure all required values are non-zero
        area_bajo_curva = get_area_under_curve(t_infusion, conc_peak, conc_basal, const_eliminacion, intervalo)
        st.markdown(f"Área bajo la curva: :green-background[**{area_bajo_curva} mg/L*hrs**]")
        
        vol_dist = get_volumen_distribucion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, dosis, t_infusion, intervalo)
        st.markdown(f"Volumen de distribución : :green-background[**{vol_dist} L**]")
        
        aclaramiento = get_aclaramiento_medicamento(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, dosis, t_infusion, intervalo)
        st.markdown(f"Aclaramiento del medicamento: :green-background[**{aclaramiento} L/h**]")
    else:
        st.markdown("Área bajo la curva: :red[**0 mg/L*hrs**]")
        st.markdown("Volumen de distribución : :red[**0 L**]")
        st.markdown("Aclaramiento del medicamento: :red[**0 L/h**]")
