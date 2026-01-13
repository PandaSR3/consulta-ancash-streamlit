import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Consulta Ancash",
    page_icon="icon.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.big-font { font-size:20px !important; font-weight: bold; }
.success { color: #28a745; font-weight: bold; }
.danger { color: #dc3545; font-weight: bold; }
.card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

    
# Configuración de la página para que se vea bien en celulares
st.set_page_config(page_title="Consulta Ancash", layout="centered")

# --- ESTILOS CSS PARA QUE PAREZCA UNA APP MÓVIL ---
st.markdown("""
    <style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .success { color: #28a745; font-weight: bold; }
    .danger { color: #dc3545; font-weight: bold; }
    .card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    try:
        ruta = "data_ancash_mayo/DATA_ANCASH_MAYO.xlsx"

        # 1️⃣ Leer Excel
        df_ancash = pd.read_excel(
            ruta,
            sheet_name="ANCASH",
            dtype={'NDOCUMENTO': str}
        )

        df_gh = pd.read_excel(
            ruta,
            sheet_name="GH",
            dtype={'DNI': str}
        )

        # 2️⃣ Normalizar columnas
        def normalizar_columnas(df):
            df.columns = (
                df.columns
                .astype(str)
                .str.upper()
                .str.strip()
                .str.replace("Á", "A")
                .str.replace("É", "E")
                .str.replace("Í", "I")
                .str.replace("Ó", "O")
                .str.replace("Ú", "U")
                .str.replace(".", "")
                .str.replace("_", " ")
            )
            return df

        df_ancash = normalizar_columnas(df_ancash)
        df_gh = normalizar_columnas(df_gh)

        return df_ancash, df_gh

    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        return None, None

# --- INTERFAZ DE USUARIO ---
st.title("📱 Consulta Rápida")
st.markdown("Sistema de verificación de clientes y solvencia.")

df_ancash, df_gh = cargar_datos()

if df_ancash is not None:
    # Área de Búsqueda
    dni_input = st.text_input("Ingrese número de DNI:", max_chars=8)
    buscar = st.button("🔍 Buscar Información", use_container_width=True)

    if buscar and dni_input:
        # 1. Buscar en Base de Datos ANCASH (Planilla)
        resultado_ancash = df_ancash[df_ancash['NDOCUMENTO'] == dni_input]
        
        # 2. Buscar en Base de Datos GH (Grupo Horizonte)
        resultado_gh = df_gh[df_gh['DNI'] == dni_input]

        if resultado_ancash.empty and resultado_gh.empty:
            st.warning("⚠️ El DNI no figura en ninguna base de datos.")
        
        else:
            # --- MOSTRAR DATOS DE PLANILLA (ANCASH) ---
            if not resultado_ancash.empty:
                perfil = resultado_ancash.iloc[0]
                
                st.markdown("### 🏛️ Datos Nacionales (Planilla)")

                st.markdown(f"""
<div class="card">
    <div><b>Nombre:</b> {perfil.get('APELLIDOS Y NOMBRES', 'N/A')}</div>
    <div><b>N° Documento:</b> {perfil.get('NDOCUMENTO', 'N/A')}</div>
    <div><b>Código Modular:</b> {perfil.get('CODMODULAR', 'N/A')}</div>
    <div><b>Cargo:</b> {perfil.get('CARGO', 'N/A')}</div>
    <div><b>Puesto:</b> {perfil.get('PUESTO', 'N/A')}</div>
    <div><b>UGEL:</b> {perfil.get('UGEL', 'N/A')}</div>
    <hr>
    <div><b>Total Haber:</b> S/ {perfil.get('THABER', '0.00')}</div>
    <div><b>Total Líquido:</b> S/ {perfil.get('TLIQUIDO', '0.00')}</div>
    <div><b>Estatus:</b> <b>{perfil.get('ESTATUS', 'N/A')}</b></div>
    <div><b>Venta:</b> {perfil.get('VENTA', 'N/A')}</div>
    <div><b>Observaciones:</b> {perfil.get('OBSERVACIONES', 'N/A')}</div>
</div>
""", unsafe_allow_html=True)
            else:
                st.info("ℹ️ No encontrado en la base de datos Nacional/Planilla.")

# --- MOSTRAR DATOS DE DEUDA (GH) ---
if not resultado_gh.empty:
    socio = resultado_gh.iloc[0]
    st.markdown("### 🏢 Datos Comerciales (Grupo Horizonte)")

    st.markdown(f"""
<div class="card" style="border-left: 5px solid #ff4b4b;">
    <div><b>DNI:</b> {socio.get('DNI', 'N/A')}</div>
    <div><b>Nombre:</b> {socio.get('NOMBRE DEL SOCIO', 'N/A')}</div>
    <div><b>Código Modular:</b> {socio.get('CODIGO MODULAR', 'N/A')}</div>
    <div><b>Cargo:</b> {socio.get('CODIGO CARGO', 'N/A')}</div>
    <hr>
    <div><b>Año de venta:</b> {socio.get('AÑO VENTA', 'N/A')}</div>
    <div><b>Tipo de venta:</b> {socio.get('T VENTA', 'N/A')}</div>
    <div><b>Monto de venta:</b> S/ {socio.get('MONTO VENTA', '0.00')}</div>
    <div><b>Saldo:</b> S/ {socio.get('SALDO', '0.00')}</div>
    <div><b>Fecha último pago:</b> {socio.get('FECHA ULT PAGO', 'N/A')}</div>
    <div><b>Condición:</b> <b>{socio.get('CONDICION', 'N/A')}</b></div>
    <div><b>UGEL:</b> {socio.get('UGEL', 'N/A')}</div>
</div>
""", unsafe_allow_html=True)
else:
    st.success("✅ No registra deuda/historial en Grupo Horizonte.")

