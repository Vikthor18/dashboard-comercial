import pandas as pd
import streamlit as st

# Configuración inicial de la página web
st.set_page_config(
    page_title="Dashboard Comercial e Inventarios",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Dashboard Comercial e Inventarios - Inteligencia de Negocios")
st.markdown(
    "Sistema inteligente para el control de stock, análisis de ventas y"
    " optimización de micro-negocios."
)
st.markdown("---")

# 1. Base de datos simulada (Simulando el inventario de un comercio local)
datos_ejemplo = {
    "Producto": [
        "Recargas Telefónicas",
        "Fundas para Celular",
        "Servicio de Copias e Impresiones",
        "Pago de Servicios",
        "Accesorios de Cómputo",
    ],
    "Categoría": [
        "Servicios",
        "Accesorios",
        "Papelería",
        "Servicios",
        "Electrónica",
    ],
    "Stock Actual": [150, 18, 500, 100, 12],
    "Stock Mínimo": [50, 20, 100, 20, 15],
    "Precio Venta (MXN)": [50.0, 150.0, 2.0, 15.0, 350.0],
    "Ventas Mensuales": [1200, 45, 3000, 250, 8],
}
df_base = pd.DataFrame(datos_ejemplo)

# 2. Panel Lateral (Filtros y Configuración)
st.sidebar.header("⚙️ Panel de Control")
opcion_vista = st.sidebar.radio(
    "Selecciona una vista:",
    ["Inventario Base del Negocio", "Cargar Datos Propios (Excel/CSV)"],
)

if opcion_vista == "Inventario Base del Negocio":
  df = df_base
else:
  st.sidebar.markdown(
      "Sube un archivo CSV con las columnas de tus propios productos."
  )
  archivo = st.sidebar.file_uploader("Cargar archivo", type=["csv", "xlsx"])
  if archivo is not None:
    if archivo.name.endswith(".csv"):
      df = pd.read_csv(archivo)
    else:
      df = pd.read_excel(archivo)
  else:
    df = df_base
    st.sidebar.info("Mostrando datos de demostración mientras subes un archivo.")

# 3. Indicadores Clave (KPIs Comerciales)
st.subheader("📌 Indicadores Clave de Desempeño (KPIs)")
col1, col2, col3 = st.columns(3)

with col1:
  st.metric(
      label="Total de Productos Registrados",
      value=len(df),
      delta="Catálogo Activo",
  )

with col2:
  if "Ventas Mensuales" in df.columns:
    total_ventas = df["Ventas Mensuales"].sum()
    st.metric(
        label="Volumen Total de Ventas", value=f"{total_ventas:,} unidades"
    )
  else:
    st.metric(label="Volumen Total de Ventas", value="N/D")

with col3:
  if "Stock Actual" in df.columns and "Stock Mínimo" in df.columns:
    alertas = len(df[df["Stock Actual"] <= df["Stock Mínimo"]])
    st.metric(
        label="Alertas de Stock Bajo",
        value=alertas,
        delta="-Reabastecer urgente" if alertas > 0 else "Stock Seguro",
        delta_color="inverse",
    )

st.markdown("---")

# 4. Tabla Interactiva de Inventario
st.subheader("📦 Control de Stock y Existencias")
st.dataframe(df, use_container_width=True)

# 5. Gráficas interactivas
st.markdown("---")
st.subheader("📈 Análisis Visual de Movimiento")
if "Producto" in df.columns and "Ventas Mensuales" in df.columns:
  st.bar_chart(df.set_index("Producto")["Ventas Mensuales"])
else:
  st.info("El archivo cargado no contiene las columnas para generar la gráfica.")

# Pie de página comercial
st.markdown("---")
st.markdown(
    "💡 *Desarrollado con Inteligencia Artificial y Python para optimización"
    " comercial.*"
)