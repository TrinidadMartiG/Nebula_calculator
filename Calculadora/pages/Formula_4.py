import streamlit as st

st.title("Calculadora de Interés Simple")

# Entradas del usuario
principal = st.number_input("Principal (Monto inicial):", min_value=0.0, format="%.2f")
rate = st.number_input("Tasa de interés anual (%):", min_value=0.0, format="%.2f")
time = st.number_input("Tiempo (en años):", min_value=0.0, format="%.2f")

# Cálculo
if st.button("Calcular Interés"):
    interest = (principal * rate * time) / 100
    st.write(f"El interés simple es: {interest:.2f}")