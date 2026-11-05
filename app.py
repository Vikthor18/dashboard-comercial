from datetime import datetime
from fpdf import FPDF
import pandas as pd
import sqlite3
import streamlit as st

# Configuración inicial de la página web
st.set_page_config(
    page_title="Dashboard Comercial e Inventarios Avanzado",
    page_icon="📊",
    layout="wide",
)


# --- 1. CONEXIÓN Y CONFIGURACIÓN DE LA BASE DE DATOS REAL (SQLite) ---
def inicializar_db():
  conn = sqlite3.connect("inventario_negocio.db")
  cursor = conn.cursor()
  # Crear tabla si no existe
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT,
            categoria TEXT,
            stock_actual INTEGER,
            stock_minimo INTEGER,
            precio REAL,
            ventas_mensuales INTEGER
        )
    """)
  conn.commit()

  # Si la tabla está vacía, insertamos datos iniciales de ejemplo
  cursor.execute("SELECT COUNT(*) FROM productos")
  if cursor.fetchone()[0] == 0:
    datos_iniciales = [
        ("Recargas Telefónicas", "Servicios", 150, 50, 50.0, 1200),
        ("Fundas para Celular", "Accesorios", 18, 20, 150.0, 45),
        ("Servicio de Copias e Impresiones", "Papelería", 500, 100, 2.0, 3000),
        ("Pago de Servicios", "Servicios", 100, 20, 15.0, 250),
        ("Accesorios de Cómputo", "Electrónica", 12, 15, 350.0, 8),
    ]
    cursor.executemany(
        """
            INSERT INTO productos (producto, categoria, stock_actual, stock_minimo, precio, ventas_mensuales)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        datos_iniciales,
    )
    conn.commit()
  conn.close()


inicializar_db()


# Funciones para interactuar con la Base de Datos
def cargar_datos_db():
  conn = sqlite3.connect("inventario_negocio.db")
  df = pd.read_sql_query("SELECT * FROM productos", conn)
  conn.close()
  return df
    
def registrar_venta_db(producto_id, cantidad_vendida):
  conn = sqlite3.connect("inventario_negocio.db")
  cursor = conn.cursor()

  # Obtenemos el stock actual y las ventas actuales del producto
  cursor.execute(
      "SELECT stock_actual, ventas_mensuales FROM productos WHERE id = ?",
      (producto_id,),
  )
  resultado = cursor.fetchone()

  if resultado:
    stock_actual, ventas_actuales = resultado
    if stock_actual >= cantidad_vendida:
      nuevo_stock = stock_actual - cantidad_vendida
      nuevas_ventas = ventas_actuales + cantidad_vendida

      # Actualizamos la base de datos
      cursor.execute(
          """
                UPDATE productos 
                SET stock_actual = ?, ventas_mensuales = ? 
                WHERE id = ?
            """,
          (nuevo_stock, nuevas_ventas, producto_id),
      )
      conn.commit()
      conn.close()
      return True
    else:
      conn.close()
      return False
  conn.close()
  return False

def agregar_producto_db(
    prod, cat, stock, stock_min, precio, ventas
):  # pylint: disable=too-many-arguments
  conn = sqlite3.connect("inventario_negocio.db")
  cursor = conn.cursor()
  cursor.execute(
      """
        INSERT INTO productos (producto, categoria, stock_actual, stock_minimo, precio, ventas_mensuales)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
      (prod, cat, stock, stock_min, precio, ventas),
  )
  conn.commit()
  conn.close()


# --- 2. GENERADOR DE REPORTES EN PDF ---
def generar_pdf(df_inventario):
  pdf = FPDF()
  pdf.add_page()
  pdf.set_font("Arial", "B", 16)
  pdf.cell(
      200,
      10,
      txt="Reporte Ejecutivo - Control de Inventarios",
      ln=True,
      align="C",
  )
  pdf.set_font("Arial", "", 10)
  pdf.cell(
      200,
      10,
      txt=f"Fecha de emisión: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
      ln=True,
      align="C",
  )
  pdf.ln(10)

  pdf.set_font("Arial", "B", 10)
  pdf.cell(60, 10, "Producto", 1)
  pdf.cell(35, 10, "Categoria", 1)
  pdf.cell(25, 10, "Stock", 1)
  pdf.cell(25, 10, "Minimo", 1)
  pdf.cell(30, 10, "Precio ($)", 1)
  pdf.ln()

  pdf.set_font("Arial", "", 10)
  for _, row in df_inventario.iterrows():
    pdf.cell(60, 10, str(row["producto"]), 1)
    pdf.cell(35, 10, str(row["categoria"]), 1)
    pdf.cell(25, 10, str(row["stock_actual"]), 1)
    pdf.cell(25, 10, str(row["stock_minimo"]), 1)
    pdf.cell(30, 10, str(row["precio"]), 1)
    pdf.ln()

  # Solución: envolvemos el resultado en bytes()
  return bytes(pdf.output(dest="S"))

# Cargar datos desde SQLite
df = cargar_datos_db()

# Panel lateral para controles y registro
st.sidebar.header("⚙️ Gestión del Negocio")
menu = st.sidebar.radio(
    "Selecciona una opción:", ["Vista General y KPIs", "Registrar Nuevo Producto"]
)

if menu == "Registrar Nuevo Producto":
  st.sidebar.subheader("➕ Agregar al Inventario SQL")
  with st.sidebar.form("form_producto"):
    nuevo_prod = st.text_input("Nombre del Producto")
    nueva_cat = st.selectbox(
        "Categoría",
        ["Servicios", "Accesorios", "Papelería", "Electrónica", "General"],
    )
    nuevo_stock = st.number_input("Stock Actual", min_value=0, value=10)
    nuevo_min = st.number_input("Stock Mínimo de Alerta", min_value=0, value=5)
    nuevo_precio = st.number_input(
        "Precio de Venta ($)", min_value=0.0, value=100.0
    )
    nuevas_ventas = st.number_input(
        "Ventas Mensuales Estimadas", min_value=0, value=50
    )

    submit = st.form_submit_button("Guardar en Base de Datos")
    if submit and nuevo_prod:
      agregar_producto_db(
          nuevo_prod,
          nueva_cat,
          nuevo_stock,
          nuevo_min,
          nuevo_precio,
          nuevas_ventas,
      )
      st.sidebar.success(f"¡Producto '{nuevo_prod}' guardado con éxito!")
      st.rerun()

# --- 4. INDICADORES CLAVE (KPIs) ---
st.subheader("📌 Indicadores Clave de Desempeño (KPIs)")
col1, col2, col3 = st.columns(3)

with col1:
  st.metric(
      label="Total de Productos Registrados",
      value=len(df),
      delta="Base SQL Activa",
  )

with col2:
  total_ventas = df["ventas_mensuales"].sum()
  st.metric(label="Volumen Total de Ventas", value=f"{total_ventas:,} unidades")

with col3:
  alertas = len(df[df["stock_actual"] <= df["stock_minimo"]])
  st.metric(
      label="Alertas de Stock Bajo",
      value=alertas,
      delta="-Reabastecer urgente" if alertas > 0 else "Stock Seguro",
      delta_color="inverse",
  )

st.markdown("---")

# --- 5. TABLA Y EXPORTACIÓN A PDF ---
st.subheader("📦 Control de Stock en Base de Datos")
st.dataframe(df, use_container_width=True)

# Botón de descarga de PDF
st.markdown("### 📄 Descargar Reporte Ejecutivo")
if not df.empty:
  pdf_bytes = generar_pdf(df)
  st.download_button(
      label="📥 Descargar Reporte de Inventario en PDF",
      data=pdf_bytes,
      file_name="reporte_inventario.pdf",
      mime="application/pdf",
  )

# --- 6. GRÁFICAS INTERACTIVAS ---
st.markdown("---")
st.subheader("📈 Análisis Visual de Movimiento")
if not df.empty:
  st.bar_chart(df.set_index("producto")["ventas_mensuales"])

st.markdown("---")
st.markdown(
    "💡 *Software de Inteligencia de Negocios optimizado para PyMEs y comercios.*"
)
