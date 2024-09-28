import streamlit as st

st.title("Conversión de Temperatura (Celsius a Fahrenheit)")

# Input de la temperatura en Celsius
celsius = st.number_input("Introduce la temperatura en Celsius:", min_value=-273.15, step=0.1)

# Conversión a Fahrenheit
fahrenheit = (celsius * 9/5) + 32

# Mostrar el resultado
st.write(f"La temperatura en Fahrenheit es: {fahrenheit:.2f} °F")