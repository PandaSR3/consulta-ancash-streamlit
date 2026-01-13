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

        # Limpieza de columnas
        df_ancash.columns = df_ancash.columns.str.strip()
        df_gh.columns = df_gh.columns.str.strip()

        return df_ancash, df_gh

    except FileNotFoundError:
        st.error("❌ No se encontró el archivo Excel. Revisa nombre y carpeta.")
        return None, None

    except Exception as e:
        st.error(f"❌ Error al leer el Excel: {e}")
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
                st.markdown("### 🏛️ Datos Laborales (Nacional)")
                with st.container():
                    st.markdown(f"""
                    <div class="card">
                        <div><b>Nombre:</b> {perfil.get('APELLIDOS Y NOMBRES', 'N/A')}</div>
                        <div><b>Cargo:</b> {perfil.get('PUESTO', 'N/A')}</div>
                        <div><b>UGEL:</b> {perfil.get('UGEL', 'N/A')}</div>
                        <hr>
                        <div><b>Total Líquido:</b> S/ {perfil.get('TLIQUIDO', '0.00')}</div>
                        <div><b>Estado:</b> <span class="{'success' if perfil.get('ESTATUS') == 'SOLVENTE' else 'danger'}">{perfil.get('ESTATUS', 'N/A')}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("ℹ️ No encontrado en la base de datos Nacional/Planilla.")

            # --- MOSTRAR DATOS DE DEUDA (GH) ---
            if not resultado_gh.empty:
                socio = resultado_gh.iloc[0]
                estado_deuda = socio.get('CONDICION', 'N/A')
                color_deuda = "danger" if "PENDIENTE" in str(estado_deuda).upper() else "success"

                st.markdown("### 🏢 Datos Grupo Horizonte")
                with st.container():
                    st.markdown(f"""
                    <div class="card" style="border-left: 5px solid #ff4b4b;">
                        <div><b>Cliente:</b> {socio.get('Nombre del Socio', 'N/A')}</div>
                        <div><b>Saldo Deuda:</b> S/ {socio.get('Saldo', '0.00')}</div>
                        <div><b>Último Pago:</b> {socio.get('Fecha Ult. Pago', 'N/A')}</div>
                        <div><b>Condición:</b> <span class="{color_deuda}">{estado_deuda}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ No registra deuda/historial en Grupo Horizonte.")
