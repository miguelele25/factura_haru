import streamlit as st
from datetime import datetime
from utils import buscar_estudiante, guardar_factura, get_conceptos_activos

st.title("🌸 FacturaRápida - Haru no Hinata")

if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    if st.text_input("Código de acceso:", type="password") == "Haru2026":
        st.session_state.autenticado = True
        st.rerun()
    st.stop()

if "cliente" not in st.session_state: st.session_state.cliente = None

st.subheader("Búsqueda de Estudiante")
col1, col2 = st.columns(2)
tipo_doc = col1.selectbox("Tipo Doc", ["CC", "PPT", "CE", "PP", "NUIP", "NIT"])
num_doc = col2.text_input("Número")

if st.button("Buscar"):
    st.session_state.cliente = buscar_estudiante(f"{tipo_doc}-{num_doc}") or {"Es_Manual": True}

if st.session_state.cliente:
    c = st.session_state.cliente
    df_eventos = get_conceptos_activos()
    
    with st.form("factura_form"):
        nombre = st.text_input("Nombre / Razón Social", value=c.get('Nombre Completo', ''))
        direccion = st.text_input("Dirección", value=c.get('Dirección', ''))
        ciudad = st.text_input("Ciudad", value=c.get('Ciudad', ''))
        telefono = st.text_input("Teléfono", value=c.get('Celular', ''))
        est_activo = st.selectbox("¿Estudiante Activo?", ["Sí", "No"], index=0 if c.get('Estado') == 'Activo' else 1)
        
        evt = st.selectbox("Evento", df_eventos['Evento'].unique().tolist())
        con = st.selectbox("Concepto", df_eventos[df_eventos['Evento'] == evt]['Concepto'].tolist())
        
        tipo_entidad = st.selectbox("Tipo de Entidad", ["Natural", "Jurídica"])
        iva = st.selectbox("¿Es Responsable de IVA?", ["No", "Sí"])
        rete = st.selectbox("¿Es Retenedor?", ["No", "Sí"])
        
        link_archivo = st.text_input("Link del Comprobante (Drive)")

        if st.form_submit_button("Guardar Factura"):
            guardar_factura({
                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Tipo_Entidad': tipo_entidad, 'Tipo_Doc': tipo_doc, 'Num_Doc': num_doc,
                'Nombre_Razon': nombre, 'Direccion': direccion, 'Ciudad': ciudad,
                'Telefono': telefono, 'Es_Responsable_IVA': iva, 'Es_Retenedor': rete,
                'Evento': evt, 'Concepto': con, 'Est_Activo': est_activo, 'Link_Archivo_Drive': "Pendiente",
                'Link_Archivo_Drive': link_archivo
            })
            st.success("¡Factura guardada!")
            st.session_state.cliente = None
            st.rerun()