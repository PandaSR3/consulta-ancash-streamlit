import streamlit as st
import pandas as pd

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(
    page_title="Consulta Ancash",
    page_icon="icon.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background-color: #ffffff !important;
    color: #111111 !important;
}

h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #111111 !important;
}

input, textarea {
    color: #111111 !important;
    background-color: #ffffff !important;
}

button {
    background-color: #2563eb !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    font-weight: bold !important;
}

.card {
    background-color: #f8fafc;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.success { color: #16a34a !important; font-weight: bold; }
.danger { color: #dc2626 !important; font-weight: bold; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def cargar_datos():
    ruta = "data_ancash_mayo/DATA_ANCASH_MAYO.xlsx"

    df_ancash = pd.read_excel(ruta, sheet_name="ANCASH", dtype={'NDOCUMENTO': str})
    df_gh = pd.read_excel(ruta, sheet_name="GH", dtype={'DNI': str})

    def normalizar(df):
        df.columns = (
            df.columns.astype(str)
            .str.upper()
            .str.strip()
            .str.replace("Á", "A")
            .str.replace("É", "E")
            .str.replace("Í", "I")
            .str.replace("Ó", "O")
            .str.replace("Ú", "U")
            .str.replace("_", " ")
            .str.replace(".", "")
        )
        return df

    return normalizar(df_ancash), normalizar(df_gh)

# ---------------- INTERFAZ ----------------
st.title("📱 Consulta Rápida")
st.markdown("Sistema de verificación de clientes y solvencia.")

df_ancash, df_gh = cargar_datos()

dni_input = st.text_input("Ingrese número de DNI:", max_chars=8)
buscar = st.button("🔍 Buscar Información", use_container_width=True)

if buscar and dni_input:
    # Buscar en ambas bases
    resultado_ancash = df_ancash[df_ancash["NDOCUMENTO"] == dni_input]
    resultado_gh = df_gh[df_gh["DNI"] == dni_input]

    if resultado_ancash.empty and resultado_gh.empty:
        st.warning("⚠️ El DNI no figura en ninguna base de datos.")
    else:
        # ================= DATOS LABORALES NACIONALES =================
        if not resultado_ancash.empty:
            perfil = resultado_ancash.iloc[0]

            estado_laboral = perfil.get('ESTATUS', 'N/A')

            estado_malo = ["SOBREGIRADO", "BLOQUEADO", "INACTIVO", "INHABILITADO"]
            color_estado = (
                "danger"
                 if str(estado_laboral).upper() in estado_malo
                else "success"
)


            st.markdown("### 🏛️ Datos Laborales Nacionales")

            st.markdown(f"""
<div class="card">
    <div><b>Nombre:</b> {perfil.get('APELLIDOS Y NOMBRES', 'N/A')}</div>
    <div><b>Puesto:</b> {perfil.get('PUESTO', 'N/A')}</div>
    <div><b>UGEL:</b> {perfil.get('UGEL', 'N/A')}</div>
    <div><b>Código Modular:</b> {perfil.get('CODMODULAR', 'N/A')}</div>
    <div><b>Cargo:</b> {perfil.get('CODIGOCARGO', 'N/A')}</div>
    <hr>
    <div><b>Ingreso Total (THABER):</b> S/ {perfil.get('THABER', '0.00')}</div>
    <div><b>Total Líquido:</b> S/ {perfil.get('TLIQUIDO', '0.00')}</div>
    <div><b>Estado:</b> <span class="{color_estado}">{estado_laboral}</span></div>

</div>
""", unsafe_allow_html=True)

        else:
            st.info("ℹ️ No figura en la base de datos nacional.")

        # ================= GRUPO HORIZONTE =================
        if not resultado_gh.empty:
            socio = resultado_gh.iloc[0]

            condicion = socio.get('CONDICION', 'N/A')
            color_condicion = (
                "danger"
                if str(condicion).upper() in ["PENDIENTE", "MOROSO", "DEUDA"]
                else "success"
            )

            fecha_pago = socio.get('FECHA ULT PAGO', 'N/A')
            if pd.notna(fecha_pago):
                try:
                    fecha_pago = pd.to_datetime(fecha_pago).strftime("%d/%m/%Y")
                except:
                    pass

            st.markdown("### 🏢 Data Grupo Horizonte")

            st.markdown(f"""
<div class="card" style="border-left: 5px solid {'#dc2626' if color_condicion == 'danger' else '#16a34a'};">
    <div><b>Cliente:</b> {socio.get('NOMBRE DEL SOCIO', 'N/A')}</div>
    <hr>
    <div><b>Monto de venta:</b> S/ {socio.get('MONTO VENTA', '0.00')}</div>
    <div><b>Saldo de deuda:</b> S/ {socio.get('SALDO', '0.00')}</div>
    <div><b>Último pago:</b> {fecha_pago}</div>
    <div><b>Condición:</b> <span class="{color_condicion}">{condicion}</span></div>
</div>
""", unsafe_allow_html=True)

        else:
            st.success("✅ No registra deuda en Grupo Horizonte.")
