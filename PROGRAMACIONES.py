import streamlit as st
import pandas as pd
from io import BytesIO
import sqlite3

# Conexión y configuración de la base de datos SQLite
def init_db():
    conn = sqlite3.connect("datos_clima_mist.db")
    cursor = conn.cursor()
    
    # Crear tablas si no existen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semana TEXT NOT NULL,
            tipo TEXT NOT NULL,
            datos BLOB NOT NULL
        )
    """)
    conn.commit()
    return conn

# Función para guardar datos en la base de datos
def guardar_datos(semana, tipo, datos):
    conn = init_db()
    cursor = conn.cursor()
    
    # Convertir el DataFrame en formato binario
    buffer = BytesIO()
    datos.to_pickle(buffer)
    datos_blob = buffer.getvalue()
    
    # Insertar o actualizar los datos en la base de datos
    cursor.execute("""
        INSERT INTO registros (semana, tipo, datos)
        VALUES (?, ?, ?)
        """, (semana, tipo, datos_blob))
    
    conn.commit()
    conn.close()

# Función para cargar datos desde la base de datos
def cargar_datos(semana, tipo):
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("SELECT datos FROM registros WHERE semana = ? AND tipo = ?", (semana, tipo))
    resultado = cursor.fetchone()
    conn.close()
    
    # Si se encuentran datos, convertirlos de vuelta a DataFrame
    if resultado:
        buffer = BytesIO(resultado[0])  # Crear un buffer a partir de los datos binarios
        return pd.read_pickle(buffer)  # Deserializar a DataFrame
    return None

# Cargar todas las semanas registradas
def cargar_semanas_disponibles():
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT semana FROM registros")
    semanas = [fila[0] for fila in cursor.fetchall()]
    conn.close()
    return semanas

# Función para borrar todos los datos de la base de datos
def borrar_todos_los_datos():
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registros")  # Elimina todos los registros de la tabla
    conn.commit()
    conn.close()

# Título de la aplicación
st.title("Aplicación para Actualizar Datos de Clima y Mist")

# Botón para eliminar todos los datos
if st.button("Borrar todos los datos y reiniciar"):
    borrar_todos_los_datos()
    st.success("Todos los datos han sido eliminados. Ahora puedes empezar desde cero.")

# Datos predefinidos para Clima y Mist
clima_data = {
    "PROGRAMA": ["PANTALLA", None, None, None, None, None, "VENTILACION 1", None, None, None, None, None, "VENTILACION 2", None, None, None, None, None, "COOLING", None, "CALEFACION"],
    "CONSIGNA": ["XIMENEIA SOLEADO", "XIMENEIA TºALTA", "XIMENEIA Tº BAJA", "CIERRE -Tº ALTA (ºC)", "CIERRE Tº BAJA (ºC)", "CIERRE SOLEADO (W/m2)", "APERTURA VENTANAS (ºC)", "RANGO REGULACION (ºC)", "VIENTO", "LLUVIA", "MAX. APERTURA", "MIN. APERTURA", "APERTURA VENTANAS (ºC)", "RANGO REGULACION (ºC)", "VIENTO", "LLUVIA", "MAX. APERTURA", "MIN. APERTURA", "BLOQUEO VENTANAS (ºC)", "Tº COOLING", "TEMPERATURA (ºC)"],
    "INVERNADERO": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
}

mist_data = {
    "GRUPO": ["INTERVALO", "RADIACION (W/m2)", "HORARIO", "ELECTROVALVULAS", "TIEMPO"],
    "1": ["-", "-", "-", "-", "-"],
    "2": ["-", "-", "-", "-", "-"],
    "3": ["-", "-", "-", "-", "-"],
    "4": ["-", "-", "-", "-", "-"],
    "5": ["-", "-", "-", "-", "-"],
    "6": ["-", "-", "-", "-", "-"],
    "7": ["-", "-", "-", "-", "-"],
    "8": ["-", "-", "-", "-", "-"],
    "9": ["-", "-", "-", "-", "-"],
    "10": ["-", "-", "-", "-", "-"],
}

# Casilla para introducir la semana y el año
semana = st.text_input("Introduce la semana y el año (formato sXX-20XX):", "s01-2024")

# Crear pestañas para Clima y Mist
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Clima R04", "Clima R02", "Clima C02", "Mist R04", "Mist R02", "Mist C02", "Comparar Semanas"])

def manejar_pestaña(semana, tipo, datos_iniciales):
    # Cargar datos guardados si existen
    datos_guardados = cargar_datos(semana, tipo)
    if datos_guardados is not None:
        datos_df = datos_guardados
    else:
        datos_df = pd.DataFrame(datos_iniciales)
    
    # Interfaz de edición con una clave única
    datos_df = st.data_editor(datos_df, use_container_width=True, key=f"{tipo}_editor_{semana}")
    
    # Botón para guardar datos con clave única
    if st.button(f"Guardar {tipo}", key=f"guardar_{tipo}_{semana}"):
        guardar_datos(semana, tipo, datos_df)
        st.success(f"Datos de {tipo} guardados para la semana {semana}")
    
    # Botón para descargar los datos con clave única
    datos_output = BytesIO()
    datos_df.to_excel(datos_output, index=False, engine="openpyxl")
    datos_output.seek(0)
    st.download_button(
        f"Descargar {tipo} Actualizado",
        datos_output,
        f"{tipo.lower()}_actualizado.xlsx",
        key=f"download_{tipo}_{semana}"
    )

with tab1:
    st.subheader("Datos del Grupo Clima R04")
    manejar_pestaña(semana, "Clima R04", clima_data)

with tab2:
    st.subheader("Datos del Grupo Clima R02")
    manejar_pestaña(semana, "Clima R02", clima_data)

with tab3:
    st.subheader("Datos del Grupo Clima C02")
    manejar_pestaña(semana, "Clima C02", clima_data)

with tab4:
    st.subheader("Datos del Grupo Mist R04")
    manejar_pestaña(semana, "Mist R04", mist_data)

with tab5:
    st.subheader("Datos del Grupo Mist R02")
    manejar_pestaña(semana, "Mist R02", mist_data)

with tab6:
    st.subheader("Datos del Grupo Mist C02")
    manejar_pestaña(semana, "Mist C02", mist_data)

with tab7:
    st.subheader("Comparar Semanas")
    semanas_disponibles = cargar_semanas_disponibles()
    
    if len(semanas_disponibles) < 2:
        st.warning("Se necesitan al menos dos semanas registradas para comparar.")
    else:
        # Selección de semanas y tipo de datos
        semana1 = st.selectbox("Selecciona la primera semana:", semanas_disponibles, key="semana1_comparar")
        semana2 = st.selectbox("Selecciona la segunda semana:", [s for s in semanas_disponibles if s != semana1], key="semana2_comparar")
        tipo = st.radio("Selecciona el tipo de datos a comparar:", ["Clima R04", "Clima R02", "Clima C02", "Mist R04", "Mist R02", "Mist C02"], key="tipo_comparar")
        
        # Cargar datos para ambas semanas
        df1 = cargar_datos(semana1, tipo)
        df2 = cargar_datos(semana2, tipo)
        
        if df1 is not None and df2 is not None:
            if df1.shape == df2.shape:
                # Crear una función para resaltar diferencias solo en la segunda semana
                def resaltar_diferencias(data):
                    styles = pd.DataFrame("", index=data.index, columns=data.columns)
                    for row in data.index:
                        for col in data.columns:
                            if df1.loc[row, col] != df2.loc[row, col]:
                                styles.loc[row, col] = "background-color: red; color: white;"
                    return styles
                
                # Mostrar tablas con diferencias resaltadas en la segunda semana
                st.write(f"### Datos de la semana {semana1}")
                st.dataframe(df1)

                st.write(f"### Datos de la semana {semana2} (celdas diferentes resaltadas en rojo)")
                st.dataframe(df2.style.set_table_styles([]).apply(resaltar_diferencias, axis=None))
            else:
                st.warning("Los DataFrames de las semanas seleccionadas tienen diferentes formas, no se pueden comparar.")
        else:
            st.warning("No se encontraron datos para las semanas seleccionadas.")
