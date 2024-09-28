import streamlit as st
import math

st.title("Cálculo del Área de un Círculo")

# Input del radio
radio = st.number_input("Introduce el radio del círculo:", min_value=0.0, step=0.1)

# Cálculo del área
area = math.pi * radio ** 2

# Mostrar el resultado
st.write(f"El área del círculo es: {area:.2f} unidades cuadradas")