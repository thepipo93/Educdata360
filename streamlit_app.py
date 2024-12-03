import streamlit as st
import gspread
from anthropic import Anthropic
from collections import defaultdict

# Configuración simple
st.set_page_config(page_title="Análisis Estudiantil", layout="centered")

def init_sheets():
    """Conecta con Google Sheets"""
    try:
        gc = gspread.service_account_from_dict(st.secrets["google_credentials"])
        return gc.open_by_key(st.secrets["SHEET_ID"])
    except Exception as e:
        st.error("Error de conexión con la base de datos.")
        return None

def get_student_data(sheet, student_name):
    """Obtiene datos del estudiante"""
    try:
        worksheet = sheet.get_worksheet(0)
        data = worksheet.get_all_records()
        return [record for record in data if student_name.lower() in record['Estudiante'].lower()]
    except Exception as e:
        st.error("Error al obtener datos")
        return None

def analyze_student(records):
    """Analiza el desempeño del estudiante"""
    try:
        client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        
        exitosas = len([r for r in records if r['Recupero?'] == 'Si'])
        pendientes = len([r for r in records if r['Recupero?'] == 'No'])
        
        prompt = f"""Analiza el siguiente historial de recuperaciones:
        
        Total materias: {len(records)}
        Recuperaciones exitosas: {exitosas}
        Recuperaciones pendientes: {pendientes}
        
        Historial completo:
        {records}
        
        Proporciona un análisis con estos puntos usando el siguiente formato exacto:

        ## Materias que más recupera
        - [Lista de materias]

        ## Materias que necesitan atención urgente
        - [Lista de materias]

        ## Progreso actual
        - Recuperaciones exitosas: [X] de [Y] ([Z]%)
        - Recuperaciones pendientes: [X] de [Y] ([Z]%)

        ## Recomendaciones
        1. [Primera recomendación]
        2. [Segunda recomendación]
        3. [Tercera recomendación]

        ## Patrones identificados
        - [Primer patrón]
        - [Segundo patrón]
        - [Tercer patrón]

        ## Conclusión
        [Breve conclusión de 2-3 líneas]
        """
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Limpiamos el texto de la respuesta
        cleaned_text = response.content
        if isinstance(cleaned_text, list):
            cleaned_text = cleaned_text[0]
        if hasattr(cleaned_text, 'text'):
            cleaned_text = cleaned_text.text
        
        # Eliminamos cualquier mención a TextBlock y type='text'
        cleaned_text = cleaned_text.replace("TextBlock(text='", "")
        cleaned_text = cleaned_text.replace("', type='text')", "")
        
        return cleaned_text

    except Exception as e:
        st.error("Error en el análisis")
        return None

def main():
    st.title("Análisis Estudiantil")
    
    # Conexión a la base de datos
    sheet = init_sheets()
    if not sheet:
        return
    
    # Interfaz de usuario
    nombre = st.text_input("Nombre del estudiante")
    
    if st.button("Analizar"):
        if nombre:
            with st.spinner('Analizando...'):
                datos = get_student_data(sheet, nombre)
                
                if datos:
                    # Métricas básicas
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Materias", len(datos))
                    with col2:
                        exitosas = len([r for r in datos if r['Recupero?'] == 'Si'])
                        st.metric("Recuperaciones Exitosas", exitosas)
                    
                    # Análisis
                    analisis = analyze_student(datos)
                    if analisis:
                        # Usamos markdown para mejor formato
                        st.markdown(analisis)
                    
                    # Datos
                    with st.expander("Ver datos completos"):
                        st.dataframe(datos)
                else:
                    st.error("No se encontraron registros")
        else:
            st.info("Ingrese el nombre del estudiante")

def main():
    st.title("Análisis Estudiantil")
    
    # Conexión a la base de datos
    sheet = init_sheets()
    if not sheet:
        return
    
    # Interfaz de usuario
    nombre = st.text_input("Nombre del estudiante")
    
    if st.button("Analizar"):
        if nombre:
            with st.spinner('Analizando...'):
                datos = get_student_data(sheet, nombre)
                
                if datos:
                    # Métricas básicas
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Materias", len(datos))
                    with col2:
                        exitosas = len([r for r in datos if r['Recupero?'] == 'Si'])
                        st.metric("Recuperaciones Exitosas", exitosas)
                    
                    # Análisis
                    analisis = analyze_student(datos)
                    if analisis:
                        st.write(analisis)
                    
                    # Datos
                    with st.expander("Ver datos completos"):
                        st.dataframe(datos)
                else:
                    st.error("No se encontraron registros")
        else:
            st.info("Ingrese el nombre del estudiante")

if __name__ == "__main__":
    main()