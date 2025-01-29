import streamlit as st
import math

# Título de la aplicación
st.title("Parámetros cinéticos 📈📉")
# Funciones

def get_dosis_dia(dosis, intervalo, peso):
    """Dosis diaria mg/kg/día"""
    formula = (dosis * (24 / intervalo)) / peso
    return round(formula, 2)

def get_const_eliminacion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2):
    """Constante de eliminación"""
    formula = math.log(conc_peak / conc_basal) / (t_ini_dosis_2 - t_ini_dosis)
    return round(formula, 3)

def get_concentracion_maxima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, t_infusion):
    """Concentración máxima real"""
    const_eliminacion = get_const_eliminacion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2)
    formula = conc_peak / math.exp(-const_eliminacion * (t_ini_dosis - t_infusion))
    return round(formula, 2)

def get_concentracion_minima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, intervalo, t_infusion):
    """Concentración mínima real"""
    conc_max_real = get_concentracion_maxima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, t_infusion)
    const_eliminacion = get_const_eliminacion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2)
    formula = conc_max_real * math.exp(-const_eliminacion * (intervalo - t_infusion))
    return round(formula, 1)

def get_aclaramiento_medicamento(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, dosis, t_infusion, intervalo):
    """Aclaramiento del medicamento"""
    vol_distribucion = get_volumen_distribucion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, dosis, t_infusion, intervalo)
    const_eliminacion = get_const_eliminacion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2)
    formula = (vol_distribucion * const_eliminacion) * 1000 / 60
    return round(formula, 2)

def get_volumen_distribucion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, dosis, t_infusion, intervalo):
    """Volumen de distribución"""
    const_eliminacion = get_const_eliminacion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2)
    conc_max_real = get_concentracion_maxima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, t_infusion)
    conc_min_real = get_concentracion_minima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, intervalo, t_infusion)
    formula = (dosis * (1 - math.exp(-const_eliminacion * t_infusion))) / (t_infusion * const_eliminacion * (conc_max_real - conc_min_real * math.exp(-const_eliminacion * t_infusion)))
    return round(formula, 2)

# Columnas para organizar la entrada de datos
col1, col_gap, col2 = st.columns([1.5, 1, 2.5])

with col1:
    # Inputs
    peso = st.number_input("Peso (kg)", min_value=1.0, value=70.0)
    dosis = st.number_input("Dosis (mg)", min_value=0, value=1000)
    st.divider()

    conc_peak = st.number_input("Concentración Peak", min_value=0.0, value=41.6)
    conc_basal = st.number_input("Concentración Basal", min_value=0.0, value=15.8)
    t_ini_dosis = st.number_input("Tiempo inicial dosis (hrs)", min_value=0.0, value=2.0)
    t_ini_dosis_2 = st.number_input("Tiempo final dosis (hrs)", min_value=0.0, value=12.0)

with col2:
    # Inputs
    talla = st.number_input("Talla (cm)", min_value=1, value=170)
    t_infusion = st.number_input("Tiempo de infusión (hrs)", min_value=0.0, value=2.0)        
    st.divider()

    intervalo = st.number_input("Intervalo entre dosis (hrs)", min_value=1, value=12)
    cim = st.number_input("Concentración mínima inhibitoria (CIM)", min_value=0.0, value=1.0)
    dosis_kg_dia = get_dosis_dia(dosis, intervalo, peso)
    st.markdown(f"Dosis (mg/kg/día): :green-background[**{dosis_kg_dia}**]")

# Mostrar resultados en la columna inferior
st.header("Resultados 🧾✍🏼")
col3, col_gap2, col4 = st.columns([1.5, 1, 2.5])

with col3:
    
    # Cálculo y visualización de la dosis diaria
    dosis_dia = get_dosis_dia(dosis, intervalo, peso)
    st.markdown(f"Dosis diaria: :green-background[**{dosis_dia} mg/kg/día**]")
    
    # Cálculo y visualización de la constante de eliminación
    const_eliminacion = get_const_eliminacion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2)
    st.markdown(f"Constante de eliminación: :green-background[**{const_eliminacion}**]")
    
with col4:
    # Cálculo y visualización de la concentración máxima real
    conc_max_real = get_concentracion_maxima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, t_infusion)
    st.markdown(f"Concentración máxima real: :green-background[**{conc_max_real} mg/L**]")
    
    # Cálculo y visualización de la concentración mínima real
    conc_min_real = get_concentracion_minima_real(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, intervalo, t_infusion)
    st.markdown(f"Concentración mínima real: :green-background[**{conc_min_real} mg/L**]")
    
    # Cálculo y visualización del volumen de distribución
    vol_dist = get_volumen_distribucion(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, dosis, t_infusion, intervalo)
    st.markdown(f"Volumen de distribución : :green-background[**{vol_dist} L**]")
    
    # Cálculo y visualización del aclaramiento del medicamento
    aclaramiento = get_aclaramiento_medicamento(conc_peak, conc_basal, t_ini_dosis, t_ini_dosis_2, dosis, t_infusion, intervalo)
    st.markdown(f"Aclaramiento del medicamento: :green-background[**{aclaramiento} L/h**]")
