import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

def get_gspread_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    for key in ["master_db_id", "facturas_db_id", "folder_id"]:
        creds_dict.pop(key, None)
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

def buscar_estudiante(id_alumno):
    client = get_gspread_client()
    sheet = client.open_by_key(st.secrets["gcp_service_account"]["master_db_id"]).worksheet("Dim_Estudiantes")
    
    data = sheet.get_all_values()
    if not data: return None
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.loc[:, df.columns != '']
    
    df['ID_Alumno'] = df['ID_Alumno'].astype(str).str.strip()
    id_limpio = str(id_alumno).strip()
    resultado = df[df['ID_Alumno'] == id_limpio]
    return resultado.iloc[0].to_dict() if not resultado.empty else None

def get_conceptos_activos():
    client = get_gspread_client()
    sheet = client.open_by_key(st.secrets["gcp_service_account"]["master_db_id"]).worksheet("Dim_Eventos")
    
    data = sheet.get_all_values()
    if not data: return pd.DataFrame()
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.loc[:, df.columns != '']
    
    return df[df['Estado'] == 'Activo']

def guardar_factura(datos_factura):
    client = get_gspread_client()
    sheet = client.open_by_key(st.secrets["gcp_service_account"]["facturas_db_id"]).sheet1
    
    # Se añade datos_factura['Cantidad'] justo después del precio unitario
    fila = [
        datos_factura['Timestamp'], datos_factura['Tipo_Entidad'], datos_factura['Tipo_Doc'],
        datos_factura['Num_Doc'], datos_factura['Nombre_Razon'], datos_factura['Direccion'],
        datos_factura['Ciudad'], datos_factura['Telefono'], datos_factura['Es_Responsable_IVA'],
        datos_factura['Es_Retenedor'], datos_factura['Evento'], datos_factura['Concepto'], 
        datos_factura['Precio'], datos_factura['Cantidad'], datos_factura['Est_Activo'], 
        datos_factura['Link_Archivo_Drive']
    ]
    sheet.append_row(fila)