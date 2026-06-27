import streamlit as st
from datetime import datetime
from utils import buscar_estudiante, guardar_factura, get_conceptos_activos

st.title("🌸 FacturaRápida - Haru no Hinata")

# --- LOGIN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    if st.text_input("Código de acceso:", type="password") == "Haru2026":
        st.session_state.autenticado = True
        st.rerun()
    st.stop()

if "cliente" not in st.session_state: st.session_state.cliente = None

# --- BÚSQUEDA ---
st.subheader("Búsqueda de Estudiante")
col1, col2 = st.columns(2)
tipo_doc = col1.selectbox("Tipo Doc", ["CC", "PPT", "CE", "PP", "NUIP", "NIT"])
num_doc = col2.text_input("Número")

if st.button("Buscar"):
    st.session_state.cliente = buscar_estudiante(f"{tipo_doc}-{num_doc}") or {"Es_Manual": True}

# --- SECCIÓN DE VERIFICACIÓN, CÁLCULO EN VIVO Y GUARDADO ---
if st.session_state.cliente:
    c = st.session_state.cliente
    df_eventos = get_conceptos_activos()
    
    st.markdown("---")
    st.subheader("Verificación de Datos del Cliente")
    
    nombre = st.text_input("Nombre / Razón Social", value=c.get('Nombre Completo', ''))
    direccion = st.text_input("Dirección", value=c.get('Dirección', ''))
    ciudad = st.text_input("Ciudad", value=c.get('Ciudad', ''))
    telefono = st.text_input("Teléfono", value=c.get('Celular', ''))
    link_archivo = st.text_input("Link del Comprobante (Drive)")
    
    col_ent, col_iva, col_ret, col_est = st.columns(4)
    tipo_entidad = col_ent.selectbox("Tipo de Entidad", ["Natural", "Jurídica"])
    iva = col_iva.selectbox("¿Es Responsable de IVA?", ["No", "Sí"])
    rete = col_ret.selectbox("¿Es Retenedor?", ["No", "Sí"])
    est_activo = col_est.selectbox("¿Estudiante Activo?", ["Sí", "No"], index=0 if c.get('Estado') == 'Activo' else 1)
    
    st.markdown("---")
    st.subheader("Selección de Productos e Información de Pago")
    
    evt = st.selectbox("Evento", df_eventos['Evento'].unique().tolist())
    df_filtrado = df_eventos[df_eventos['Evento'] == evt]
    
    conceptos_sel = st.multiselect("Conceptos / Actividades", df_filtrado['Concepto'].tolist())
    
    total_pagar = 0.0
    items_a_guardar = []
    columna_costo = 'Costo_estudiante_IVA' if est_activo == "Sí" else 'Costo_IVA'
    
    if conceptos_sel:
        st.write("#### Ajustar Cantidades:")
        for concepto in conceptos_sel:
            fila_producto = df_filtrado[df_filtrado['Concepto'] == concepto]
            if not fila_producto.empty:
                try:
                    precio_unid = float(fila_producto.iloc[0][columna_costo])
                except:
                    precio_unid = 0.0
                
                col_item, col_cant = st.columns([3, 1])
                with col_item:
                    st.markdown(f"🔹 **{concepto}** *(Unitario: ${precio_unid:,.2f})*")
                with col_cant:
                    cantidad = st.number_input(
                        f"Cantidad para {concepto}", 
                        min_value=1, 
                        value=1, 
                        step=1, 
                        key=f"cant_{concepto}",
                        label_visibility="collapsed"
                    )
                
                total_pagar += precio_unid * cantidad
                items_a_guardar.append({'concepto': concepto, 'precio': precio_unid, 'cantidad': cantidad})
    
    if conceptos_sel:
        st.write("---")
        st.metric(label="Total General a Pagar (COP)", value=f"${total_pagar:,.2f}")
    
    if st.button("Confirmar y Guardar Factura", type="primary"):
        if not conceptos_sel:
            st.error("Por favor, selecciona al menos un concepto antes de guardar el registro.")
        else:
            timestamp_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Ahora guarda una sola fila por cada tipo de producto seleccionado
            for item in items_a_guardar:
                guardar_factura({
                    'Timestamp': timestamp_actual, 'Tipo_Entidad': tipo_entidad, 'Tipo_Doc': tipo_doc, 
                    'Num_Doc': num_doc, 'Nombre_Razon': nombre, 'Direccion': direccion, 'Ciudad': ciudad,
                    'Telefono': telefono, 'Es_Responsable_IVA': iva, 'Es_Retenedor': rete,
                    'Evento': evt, 'Concepto': item['concepto'], 'Precio': item['precio'],
                    'Cantidad': item['cantidad'], 'Est_Activo': est_activo, 'Link_Archivo_Drive': link_archivo
                })
                    
            st.success(f"¡Excelente! Factura guardada. Se registraron {len(items_a_guardar)} productos en la base de datos.")
            st.session_state.cliente = None
            st.rerun()