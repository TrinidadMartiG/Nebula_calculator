import streamlit as st

st.title("Cálculo del Índice de Masa Corporal (IMC)")

# Input del peso y la altura
peso = st.number_input("Introduce tu peso en kilogramos (kg):", min_value=0.0, step=0.1)
altura = st.number_input("Introduce tu altura en metros (m):", min_value=0.0, step=0.01)

# Cálculo del IMC
if altura > 0:
    imc = peso / (altura ** 2)
    st.write(f"Tu IMC es: {imc:.2f}")
else:
    st.write("Por favor, introduce una altura válida.")