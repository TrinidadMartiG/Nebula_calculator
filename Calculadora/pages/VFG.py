import streamlit as st

# Configuración de la página
st.title("Calculadora VFG")

# Inputs comunes
col1, col2 = st.columns([2, 2])  # Crear dos columnas

with col1:  # Columna para inputs
    # Inputs para las fórmulas
    st.header("Selecciona una fórmula")
    formula_opcion = st.selectbox(
        "Fórmulas disponibles:",
        ["Clearance de creatinina (Cockcroft-Gault)", 
         "VFG no normalizada (CKD-EPI 2021)", 
         "VFG no normalizada (CKD-EPI-cistatina 2021)",
         "BIS 1"]
    )
    edad = st.number_input("Edad (años)", min_value=0 )
    peso = st.number_input("Peso (kg)", min_value=0.0 )
    talla = st.number_input("Talla (cm)", min_value=0.0)
    genero = st.selectbox("Género", ["masculino", "femenino"])
    creatinina = st.number_input("Creatinina (mg/dL)", min_value=0.0)
    if formula_opcion == "VFG no normalizada (CKD-EPI-cistatina 2021)":
        cistatina = st.number_input("Cistatina (mg/dL)", min_value=0.0)

# Funciones de cálculo
DECIMALS = 3

def bis1(creatinina, edad, genero):
    """ VFG BIS 1"""
    multi_genero = 1 if genero == "masculino" else 0.82
    formula = 3736 * (creatinina ** -0.87) * (edad ** -0.95) * multi_genero
    return round(formula, 1)

def get_peso_magro(genero, peso, imc):
    if genero == "masculino":
        ind1 = 6680
        ind2 = 216
    else:
        ind1 = 6780
        ind2 = 244
    formula = (9270 * peso) / (ind1 + (ind2 * imc))
    return round(formula, DECIMALS)

def get_imc(peso, talla):
    return round(peso / ((talla * talla) / 10000), DECIMALS)

def get_superficie_corp(peso, talla):
    return (peso ** 0.425) * (talla ** 0.725) * 0.007184

def get_cg_clearance_creatinina(edad, peso, talla, genero, creatinina):
    imc = get_imc(peso, talla)
    _peso = None
    multi_genero = 1 if genero == "masculino" else 0.85
    if imc > 30:
        _peso = get_peso_magro(genero, peso, imc)
    else:
        _peso = peso
    total = ((140 - edad) * _peso / (72 * creatinina)) * multi_genero
    return round(total, 1)

def get_cg_estimacion_vfg(edad, peso, talla, genero, creatinina):
    superficie_corp = get_superficie_corp(peso, talla)
    clear_creatinina = get_cg_clearance_creatinina(edad, peso, talla, genero, creatinina)
    return round((1.73 / superficie_corp) * clear_creatinina, 1)

def get_cdk_epicreatinina_2021(creatinina, genero, edad):
    if genero == "masculino":
        var_genero_a = 0.9
        multi_genero = 1
        if creatinina <= 0.9:
            var_genero_b = -0.302
        else:
            var_genero_b = -1.2
    else:
        var_genero_a = 0.7
        multi_genero = 1.012
        if creatinina <= 0.7:
            var_genero_b = -0.241
        else:
            var_genero_b = -1.2
    formula = 142 * ((creatinina / var_genero_a) ** var_genero_b) * (0.9938 ** edad) * multi_genero
    return round(formula, 1)

def get_vfg_no_normalizada(creatinina, genero, edad, peso, talla):
    cdk_epicreatinina_2021 = get_cdk_epicreatinina_2021(creatinina, genero, edad)
    superficie_corp = get_superficie_corp(peso, talla)
    formula = (superficie_corp / 1.73) * cdk_epicreatinina_2021
    return round(formula, 1)

def get_ckd_epicrea_cys_2021(creatinina, cistatina, genero, edad):
    multi_genero = 1 if genero == "masculino" else 0.963
    if genero == "masculino":
        if creatinina <= 0.9:
            if cistatina <= 0.8:
                A = 0.9
                B = -0.144
                C = 0.8
                D = -0.323
            else:
                A = 0.9
                B = -0.144
                C = 0.8
                D = -0.778
        else:
            if cistatina <= 0.8:
                A = 0.9
                B = -0.544
                C = 0.8
                D = -0.323
            else:
                A = 0.9
                B = -0.544
                C = 0.8
                D = -0.778
    else:
        if creatinina <= 0.7:
            if cistatina <= 0.8:
                A = 0.7
                B = -0.219
                C = 0.8
                D = -0.323
            else:
                A = 0.7
                B = -0.219
                C = 0.8
                D = -0.778
        else:
            if cistatina <= 0.8:
                A = 0.7
                B = -0.544
                C = 0.8
                D = -0.323
            else:
                A = 0.7
                B = -0.544
                C = 0.8
                D = -0.778
    formula = 135 * ((creatinina / A) ** B) * ((cistatina / C) ** D) * (0.9961 ** edad) * multi_genero
    return round(formula, 1)

def get_ckd_epicrea_cys_vfg_no_norm(creatinina, cistatina, genero, edad, peso, talla):
    estimacion_vfg = get_ckd_epicrea_cys_2021(creatinina, cistatina, genero, edad)
    superficie_corp = get_superficie_corp(peso, talla)
    formula = (superficie_corp / 1.73) * estimacion_vfg
    return round(formula, 1)

# Cálculos y resultados según la fórmula seleccionada
resultados = {}  # Diccionario para almacenar resultados

# Verificación de entradas antes de realizar cálculos
if edad <= 0 or peso <= 0 or talla <= 0 or creatinina <= 0 or cistatina <=0:
    st.warning("Por favor, asegúrate de que todos los valores sean mayores que cero.")
else:
    if formula_opcion == "Clearance de creatinina (Cockcroft-Gault)":
        clear_creatinina = get_cg_clearance_creatinina(edad, peso, talla, genero, creatinina)
        estimacion_vfg = get_cg_estimacion_vfg(edad, peso, talla, genero, creatinina)
        resultados["Clearance de creatinina"] = f"{clear_creatinina} mL/min"
        resultados["Estimación de VFG"] = f"{estimacion_vfg} mL/min/1.73m²"

    elif formula_opcion == "VFG no normalizada (CKD-EPI 2021)":
        vfg_no_normalizada = get_vfg_no_normalizada(creatinina, genero, edad, peso, talla)
        resultados["VFG no normalizada"] = f"{vfg_no_normalizada} mL/min/1.73m²"

    elif formula_opcion == "VFG no normalizada (CKD-EPI-cistatina 2021)":
        vfg_no_normalizada_cistatina = get_ckd_epicrea_cys_vfg_no_norm(creatinina, cistatina, genero, edad, peso, talla)
        resultados["VFG no normalizada (CKD-EPI-cistatina)"] = f"{vfg_no_normalizada_cistatina} mL/min/1.73m²"

    elif formula_opcion == "BIS 1":
        vfg_bis1 = bis1(creatinina, edad, genero)
        resultados["VFG BIS 1"] = f"{vfg_bis1} mL/min"

# Mostrar resultados
with col2:  # Columna para resultados
    st.subheader("Resultados")  # Encabezado de resultados
    for key, value in resultados.items():
        st.write(f"{key}: {value}")
