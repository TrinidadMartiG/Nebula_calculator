import streamlit as st
import math

def clear_inputs():
    # Reset all input values to 0
    st.session_state['peso'] = 0.0
    st.session_state['talla'] = 0
    st.session_state['dosis'] = 0
    st.session_state['intervalo'] = 0
    st.session_state['conc_peak'] = 0.00
    st.session_state['conc_basal'] = 0.00
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
    peso = st.number_input("Peso (kg)", min_value=0.0, step=1.0, format="%.1f", key='peso')
    st.divider()
    dosis = st.number_input("Dosis (mg)", min_value=0, format="%d", key='dosis')
    intervalo = st.number_input("Intervalo entre dosis (hrs)", min_value=0, format="%d", key='intervalo')
    st.divider()
    conc_peak = st.number_input("Concentración 1 (Peak) mcg/mL ", min_value=0.00, step=0.01, format="%.2f", key='conc_peak')
    conc_basal = st.number_input("Concentración 2 (Basal) mcg/mL", min_value=0.00, step=0.01, format="%.2f", key='conc_basal')

with col2:
    talla = st.number_input("Talla (cm)", min_value=0, format="%d", key='talla')
    st.divider()
    t_infusion = st.number_input("Tiempo de infusión (hrs)", min_value=0.0, step=1.0, format="%.1f", key='t_infusion')        
    
    # Add validation before calculating dosis_kg_dia
    if intervalo != 0 and peso != 0:
        dosis_kg_dia = get_dosis_dia(dosis, intervalo, peso)
        st.write(f"Dosis(mg/kg/día): :green-background[**{dosis_kg_dia}**]")
    else:
        st.write("Dosis(mg/kg/día): :red[**0**]")
    st.write(" ")
    st.divider()
    t_ini_dosis = st.number_input("Tiempo 1 (Peak - hrs)", min_value=0.0, step=1.0, format="%.1f", key='t_ini_dosis')
    t_ini_dosis_2 = st.number_input("Tiempo 2 (Basal - hrs)", min_value=0.0, step=1.0, format="%.1f", key='t_ini_dosis_2')

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

# Add this function before the results section
def mostrar_resultado(nombre, valor, unidad=""):
    if valor is None or valor == 0:
        # Texto en rojo si el valor es None o cero
        st.markdown(f"{nombre}: :red-background[**Sin resultado**]")
    else:
        # Texto en verde si el valor tiene un resultado
        st.markdown(f"{nombre}: :green-background[**{valor} {unidad}**]")

# Replace the results section with:
st.write(" ")

with st.container():
    col_title, col_button = st.columns([4, 1])
    with col_title:
        st.header("Resultados 🧾")
    with col_button:
        st.write(" ")
        st.button("Limpiar valores", on_click=clear_inputs, type="primary")
        
col3, col_gap2, col4 = st.columns([1.5, 1, 1.5])

with col3:
    # Calculate and display constant elimination
    const_eliminacion = get_const_eliminacion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2)
    mostrar_resultado("Constante de eliminación", const_eliminacion, "h-1")

    # Calculate and display real maximum concentration
    conc_max_real = get_concentracion_maxima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, t_infusion)
    mostrar_resultado("Concentración máxima real", conc_max_real, "mcg/mL")
    
    # Calculate and display real minimum concentration
    conc_min_real = get_concentracion_minima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, intervalo, t_infusion)
    mostrar_resultado("Concentración mínima real", conc_min_real, "mcg/mL")
    
with col4:
    if validate_inputs():
        # Calculate and display area under curve
        area_bajo_curva = get_area_under_curve(t_infusion, conc_peak, conc_basal, const_eliminacion, intervalo)
        mostrar_resultado("Área bajo la curva", area_bajo_curva, "mg/L*hrs")
        
        # Calculate and display distribution volume
        vol_dist = get_volumen_distribucion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, dosis, t_infusion, intervalo)
        mostrar_resultado("Volumen de distribución", vol_dist, "L")
        
        # Calculate and display drug clearance
        aclaramiento = get_aclaramiento_medicamento(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, dosis, t_infusion, intervalo)
        mostrar_resultado("Aclaramiento del medicamento", aclaramiento, "L/h")
    else:
        mostrar_resultado("Área bajo la curva", None)
        mostrar_resultado("Volumen de distribución", None)
        mostrar_resultado("Aclaramiento del medicamento", None)
