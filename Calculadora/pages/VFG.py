import streamlit as st

# Configuración de la página
st.title("Calculadora VFG 📊")

# Inputs comunes en dos columnas
col1, col2 = st.columns(2)

def clear_inputs():
    # Reset all input values to 0
    st.session_state['edad'] = 0
    st.session_state['peso'] = 0.0
    st.session_state['talla'] = 0.0
    st.session_state['creatinina'] = 0.0
    st.session_state['cistatina'] = 0.0
    st.session_state['genero'] = "masculino"

with col1:
    edad = st.number_input("Edad (años)", min_value=0, value=0, step=1, format="%d", key='edad')
    peso = st.number_input("Peso (kg)", min_value=0.0, value=0.0, step=1.0, format="%.0f", key='peso')
    genero = st.selectbox("Género", ["masculino", "femenino"], key='genero')

with col2:
    talla = st.number_input("Talla (cm)", min_value=0.0, value=0.0, step=1.0, format="%.0f", key='talla')
    creatinina = st.number_input("Creatinina (mg/dL)", min_value=0.0, value=0.0, step=0.01, format="%.2f", key='creatinina')
    cistatina = st.number_input("Cistatina (mg/dL)", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="cistatina")

st.button("Limpiar valores", on_click=clear_inputs, type="primary")

# Constantes y variables
DECIMALS = 1

# Funciones de cálculo
def bis1(creatinina, edad, genero):
    """ VFG BIS 1"""
    try:
        if creatinina <= 0 or edad <= 0:
            return None
        multi_genero = 1 if genero == "masculino" else 0.82
        formula = 3736 * (creatinina ** -0.87) * (edad ** -0.95) * multi_genero
        return round(formula, 1)
    except:
        return None

def get_peso_magro(genero, peso, imc):
    if genero == "masculino":
        ind1 = 6680
        ind2 = 216
    else:
        ind1 = 6780
        ind2 = 244
    formula = (9270 * peso) / (ind1 + (ind2 * imc))
    return round(formula, DECIMALS)

# Función para calcular el IMC con manejo de errores
def get_imc(peso, talla):
    try:
        if peso is None or talla is None or talla == 0:
            raise ValueError("Ingrese los valores del paciente.")
        return round(peso / ((talla * talla) / 10000), DECIMALS)
    except ValueError as e:
        st.error(str(e))
        return None

def get_superficie_corp(peso, talla):
    return (peso ** 0.425) * (talla ** 0.725) * 0.007184

def get_cg_clearance_creatinina(edad, peso, talla, genero, creatinina):
    imc = get_imc(peso, talla)
    _peso = get_peso_magro(genero, peso, imc) if imc > 30 else peso
    multi_genero = 1 if genero == "masculino" else 0.85
    total = ((140 - edad) * _peso / (72 * creatinina)) * multi_genero
    return round(total, 1)

def get_cg_estimacion_vfg(edad, peso, talla, genero, creatinina):
    superficie_corp = get_superficie_corp(peso, talla)
    clear_creatinina = get_cg_clearance_creatinina(edad, peso, talla, genero, creatinina)
    return round((1.73 / superficie_corp) * clear_creatinina, 1)

def get_cdk_epicreatinina_2021(creatinina, genero, edad):
    if genero == "masculino":
        var_genero_a, multi_genero = 0.9, 1
        var_genero_b = -0.302 if creatinina <= 0.9 else -1.2
    else:
        var_genero_a, multi_genero = 0.7, 1.012
        var_genero_b = -0.241 if creatinina <= 0.7 else -1.2
    formula = 142 * ((creatinina / var_genero_a) ** var_genero_b) * (0.9938 ** edad) * multi_genero
    return round(formula, 1)

def get_vfg_no_normalizada(creatinina, genero, edad, peso, talla):
    cdk_epicreatinina_2021 = get_cdk_epicreatinina_2021(creatinina, genero, edad)
    superficie_corp = get_superficie_corp(peso, talla)
    formula = (superficie_corp / 1.73) * cdk_epicreatinina_2021
    return round(formula, 1)

def get_ckd_epicrea_cys_2021(creatinina, cistatina, genero, edad):
    if cistatina <= 0:
        # Return None or some indication that the result is unavailable
        return None
    multi_genero = 1 if genero == "masculino" else 0.963
    if genero == "masculino":
        if creatinina <= 0.9:
            A, B = 0.9, -0.144
            C, D = (0.8, -0.323) if cistatina <= 0.8 else (0.8, -0.778)
        else:
            A, B = 0.9, -0.544
            C, D = (0.8, -0.323) if cistatina <= 0.8 else (0.8, -0.778)
    else:
        if creatinina <= 0.7:
            A, B = 0.7, -0.219
            C, D = (0.8, -0.323) if cistatina <= 0.8 else (0.8, -0.778)
        else:
            A, B = 0.7, -0.544
            C, D = (0.8, -0.323) if cistatina <= 0.8 else (0.8, -0.778)
    formula = 135 * ((creatinina / A) ** B) * ((cistatina / C) ** D) * (0.9961 ** edad) * multi_genero
    return round(formula, 1)

def get_ckd_epicrea_cys_vfg_no_norm(creatinina, cistatina, genero, edad, peso, talla):
    estimacion_vfg = get_ckd_epicrea_cys_2021(creatinina, cistatina, genero, edad)
    superficie_corp = get_superficie_corp(peso, talla)
    formula = (superficie_corp / 1.73) * estimacion_vfg
    return round(formula, 1)

# Cálculo de IMC
imc = get_imc(peso, talla)
# Alerta para peso magro si el IMC es mayor a 30
if imc and imc > 30:
    st.warning(f"Paciente con IMC de {imc}. Preferir Cockcroft-Gault 📢🚨❗")
    st.warning(f"Peso magro: {get_peso_magro(genero, peso, imc)} Kg ❗")
# Inicializa resultados
clear_creatinina  = estimacion_vfg_cg = estimacion_vfg = estimacion_vfg_cys = vfg_no_normalizada = vfg_no_normalizada_cistatina = bis_1_resultado = None

# Verificación de condiciones y cálculos
if edad > 0 and peso > 0 and talla > 0 and creatinina > 0:
    clear_creatinina = get_cg_clearance_creatinina(edad, peso, talla, genero, creatinina)
    estimacion_vfg_cg = get_cg_estimacion_vfg(edad, peso, talla, genero, creatinina)
    
    vfg_no_normalizada = get_vfg_no_normalizada(creatinina, genero, edad, peso, talla)
    estimacion_vfg = get_cdk_epicreatinina_2021(creatinina, genero, edad)
    estimacion_vfg_cys = get_ckd_epicrea_cys_2021(creatinina, cistatina, genero, edad)
    if cistatina > 0:
        vfg_no_normalizada_cistatina = get_ckd_epicrea_cys_vfg_no_norm(creatinina, cistatina, genero, edad, peso, talla)
    # BIS-1 solo para pacientes <= 70 años
    if edad <= 70 and creatinina > 0:
        bis_1_resultado = bis1(creatinina, edad, genero)

# Función para mostrar resultados con color
def mostrar_resultado(nombre, valor, unidad="mL/min/1.73m²"):
    if valor is None:
        # Texto en rojo si el valor es None
        st.markdown(f"{nombre}:  :red-background[**Sin resultado**]")
    else:
        # Texto en verde si el valor tiene un resultado
        st.markdown(f"{nombre}: :green-background[**{valor} {unidad}**]")

# Definir el diseño de subcolumnas con títulos
st.markdown("### Cockcroft-Gault")
col_a, col_b = st.columns(2)
with col_a:
    mostrar_resultado("Estimación de VFG", estimacion_vfg_cg)
with col_b:
    mostrar_resultado("Clearance de creatinina", clear_creatinina, "mL/min")

st.markdown("### CKD-EPI Creatinina (2021)")
col_c, col_d = st.columns(2)
with col_c:
    mostrar_resultado("Estimación VFG", estimacion_vfg)
with col_d:
    mostrar_resultado("VFG no normalizada", vfg_no_normalizada, "mL/min")

st.markdown("### CKD-EPI Crea-cys (2021)")
col_e, col_f = st.columns(2)
with col_e:
    mostrar_resultado("Estimación VFG", estimacion_vfg_cys)
with col_f:
    mostrar_resultado("VFG no normalizada", vfg_no_normalizada_cistatina, "mL/min")

st.markdown("### BIS-1")
col_e = st.columns(1)[0]
with col_e:
    mostrar_resultado("VFG BIS 1", bis_1_resultado)
