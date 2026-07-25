import streamlit as st
import geemap.foliumap as geemap
import ee
import pandas as pd
import geopandas as gpd
import numpy as np
import os, json, tempfile
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# --- 1. CONFIGURAZIONE PAGINA E STATO ---
st.set_page_config(page_title="PySTGEE", layout="wide")

if 'training_df' not in st.session_state:
    st.session_state.training_df = None
if 'prediction_df' not in st.session_state:
    st.session_state.prediction_df = None
if 'model' not in st.session_state:
    st.session_state.model = None
if 'map_layers' not in st.session_state:
    st.session_state.map_layers = [] # Per salvare i layer della mappa

EE_PROJECT = 'ee-gabrielenicolanapoli'
DATE_COLUMN = 'formatted_'
SELECTED_METRICS_USER = ['Elevation', 'Slope', 'Northness', 'Eastness', 'PlanCurvature', 'ProfileCurvature']
CATEGORICAL_METRICS = ['LULCmajor', 'Litho']

# --- 2. AUTENTICAZIONE EARTH ENGINE TRAMITE SECRETS ---
@st.cache_resource
def init_ee():
    try:
        if "EARTHENGINE_TOKEN" in st.secrets:
            creds_dict = dict(st.secrets["EARTHENGINE_TOKEN"])
            credentials = ee.ServiceAccountCredentials(
                creds_dict['client_email'], 
                key_data=json.dumps(creds_dict)
            )
            ee.Initialize(credentials, project=EE_PROJECT)
            return True
    except Exception as e:
        st.error(f"Errore di autenticazione EE: {e}")
        return False

ee_ready = init_ee()

# =====================================================================
# INCOLLA QUI LE TUE FUNZIONI DELLA CELLA 3, 4 E 5 DEL NOTEBOOK:
# - extract_covariates_fast()
# - download_rainfall_data()
# - predict_spacetime()
# - encode_categoricals()
# (Nascondo il codice delle funzioni per brevità, INCOLLALE ESATTAMENTE COME SONO NEL NOTEBOOK)
# =====================================================================

# --- 3. INTERFACCIA UTENTE (SIDEBAR) ---
st.sidebar.title("PySTGEE - Menu")

# Caricamento File Vettoriali
st.sidebar.subheader("1. Caricamento Dati")
uploaded_files = st.sidebar.file_uploader("Carica GeoJSON/Shapefile", accept_multiple_files=True)

if uploaded_files:
    # Salva i file caricati in una cartella temporanea
    temp_dir = tempfile.mkdtemp()
    file_names = []
    for f in uploaded_files:
        path = os.path.join(temp_dir, f.name)
        with open(path, "wb") as f_out:
            f_out.write(f.getbuffer())
        if f.name.endswith(('.geojson', '.shp')):
            file_names.append(f.name)
            
    st.sidebar.success(f"{len(file_names)} file caricati pronti.")
    
    # Selettori per Area e Punti
    train_sel = st.sidebar.selectbox("Seleziona Area di Training:", file_names)
    pred_sel = st.sidebar.selectbox("Seleziona Area di Predizione:", file_names)
    points_sel = st.sidebar.selectbox("Seleziona File Punti (Frane):", file_names)

    # --- BOTTONI DI ANALISI ---
    st.sidebar.subheader("2. Analisi Spaziale")
    
    if st.sidebar.button("1. Calcola Morfometria"):
        with st.spinner("Estrazione covariate da Google Earth Engine..."):
            # Qui chiami la logica di 'on_morphometry_click'
            # st.session_state.training_df = ... 
            st.success("Morfometria completata!")

    if st.sidebar.button("2. Calibra Modello"):
        with st.spinner("Addestramento Random Forest..."):
            if st.session_state.training_df is not None:
                # Qui chiami la logica di 'on_calib_click'
                # st.session_state.model = rf
                st.success("Modello calibrato con successo!")
            else:
                st.error("Devi prima calcolare la morfometria.")

    if st.sidebar.button("3. Lancia Predizione"):
        target_date = st.sidebar.date_input("Data Predizione:")
        with st.spinner("Calcolo suscettibilità dinamica..."):
            if st.session_state.model is not None:
                # Qui chiami la logica di 'predict_spacetime'
                # result_df = predict_spacetime(...)
                st.success(f"Predizione completata per {target_date}!")
            else:
                st.error("Devi prima calibrare il modello.")

# --- 4. MAPPA PRINCIPALE ---
st.title("Mappa Interattiva")

# Creazione della mappa geemap usando folium (compatibile con Streamlit)
m = geemap.Map(center=[41.0, 15.0], zoom=6)

# Aggiunta di eventuali layer calcolati
for layer in st.session_state.map_layers:
    # Esempio: m.add_gdf(layer['gdf'], layer_name=layer['name'])
    pass

# Mostra la mappa a tutto schermo in Streamlit
m.to_streamlit(height=700)
