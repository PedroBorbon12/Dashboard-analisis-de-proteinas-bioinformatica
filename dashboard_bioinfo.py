import streamlit as st
import py3Dmol
import stmol
import requests
from stmol import showmol
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de análisis de proteínas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado con mejores contrastes y visibilidad
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .metric-label {
        color: #0f1116;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #0066cc;
        font-size: 1.5rem;
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #0066cc;
        font-weight: bold;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 16px;
        color: #2c3e50;
    }
    </style>
""", unsafe_allow_html=True)

def get_protein_info(pdb_id):
    try:
        url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Obtener información detallada
            struct_url = f"https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb_id}/1"
            struct_response = requests.get(struct_url)
            struct_data = struct_response.json() if struct_response.status_code == 200 else {}
            
            return {
                "Nombre": data.get("struct", {}).get("title", "No disponible"),
                "Peso Molecular": f"{data.get('rcsb_entry_info', {}).get('molecular_weight', 'No disponible')} Da",
                "Número de Cadenas": data.get("rcsb_entry_info", {}).get("polymer_entity_count_protein", "No disponible"),
                "Resolución": f"{data.get('rcsb_entry_info', {}).get('resolution_combined', 'No disponible')} Å",
                "Método Experimental": data.get("exptl", [{}])[0].get("method", "No disponible"),
                "Organismo": struct_data.get("rcsb_entity_source_organism", [{}])[0].get("organism_scientific_name", "No disponible")
            }
    except Exception as e:
        st.error(f"Error al obtener información de la proteína: {str(e)}")
        return None

def render_3d_structure(pdb_id):
    # Obtener la estructura PDB
    url = f'https://files.rcsb.org/view/{pdb_id}.pdb'
    response = requests.get(url)
    if response.status_code == 200:
        # Crear el visualizador
        view = py3Dmol.view(width=800, height=500)
        
        # Agregar la estructura
        view.addModel(response.text, "pdb")
        
        # Estilo de la proteína
        view.setStyle({'cartoon': {'color': 'spectrum'}})
        
        # Agregar cuadrícula y ejes
        view.addUnitCell()  # Agregar celda unitaria si está disponible
        
        # Agregar ejes de referencia
        view.addLine({
            'start': {'x': 0, 'y': 0, 'z': 0},
            'end': {'x': 20, 'y': 0, 'z': 0},
            'color': 'red'
        })  # Eje X
        view.addLine({
            'start': {'x': 0, 'y': 0, 'z': 0},
            'end': {'x': 0, 'y': 20, 'z': 0},
            'color': 'green'
        })  # Eje Y
        view.addLine({
            'start': {'x': 0, 'y': 0, 'z': 0},
            'end': {'x': 0, 'y': 0, 'z': 20},
            'color': 'blue'
        })  # Eje Z
        
        # Agregar cuadrícula de fondo
        for i in range(-20, 21, 5):
            # Líneas paralelas al eje X
            view.addLine({
                'start': {'x': -20, 'y': i, 'z': 0},
                'end': {'x': 20, 'y': i, 'z': 0},
                'color': 'gray',
                'opacity': 0.4
            })
            # Líneas paralelas al eje Y
            view.addLine({
                'start': {'x': i, 'y': -20, 'z': 0},
                'end': {'x': i, 'y': 20, 'z': 0},
                'color': 'gray',
                'opacity': 0.4
            })

        # Configurar la vista
        view.zoomTo()
        
        # Agregar etiquetas para los ejes
        view.addLabel("X", {'position': {'x': 22, 'y': 0, 'z': 0}, 'color': 'red', 'fontSize': 14})
        view.addLabel("Y", {'position': {'x': 0, 'y': 22, 'z': 0}, 'color': 'green', 'fontSize': 14})
        view.addLabel("Z", {'position': {'x': 0, 'y': 0, 'z': 22}, 'color': 'blue', 'fontSize': 14})
        
        # Agregar escala en Angstroms
        view.addLabel("10Å", {'position': {'x': 10, 'y': -2, 'z': 0}, 'color': 'black', 'fontSize': 12})
        view.addLabel("20Å", {'position': {'x': 20, 'y': -2, 'z': 0}, 'color': 'black', 'fontSize': 12})
        
        return view
    return None

# Título principal
st.title("🔬Dashboard de análisis de proteínas")
st.sidebar.title("🔍Buscar Proteína")

# Input para el ID de la proteína
pdb_id = st.sidebar.text_input("Ingrese el ID de la proteína (PDB):", "1ubq").strip()

if pdb_id:
    protein_info = get_protein_info(pdb_id)
    
    if protein_info:
        # Detalles de la proteína
        st.header("🧬Detalles de la proteína")
        
        # Crear dos columnas para los indicadores
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Peso Molecular", protein_info["Peso Molecular"])
            st.metric("Número de Cadenas", protein_info["Número de Cadenas"])
            
        with col2:
            st.metric("Resolución", protein_info["Resolución"])
            st.metric("Método Experimental", protein_info["Método Experimental"])
        
        # Visualización 3D
        st.header("Visualización 3D de la proteína")
try:
    view = render_3d_structure(pdb_id)
    if view:
        # Agregar controles adicionales
        col1, col2 = st.columns(2)
        with col1:
            st.write("🔴 Eje X - Rojo")
            st.write("🟢 Eje Y - Verde")
            st.write("🔵 Eje Z - Azul")
        with col2:
            st.write("📏 Cuadrícula: 5Å por división")
            st.write("🔍 Use el mouse para rotar y hacer zoom")
        
        showmol(view, height=500, width=800)
        
        # Agregar leyenda
        st.caption("La cuadrícula muestra divisiones de 5Å. Los ejes X(rojo), Y(verde) y Z(azul) tienen marcas cada 10Å.")
except Exception as e:
    st.error(f"Error al cargar la visualización 3D: {str(e)}")
else:
    st.info("👆 Por favor, ingrese un ID de PDB válido en la barra lateral.")

