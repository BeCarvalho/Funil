import streamlit as st
import subprocess
import datetime
import re
from st_supabase_connection import SupabaseConnection
import leafmap.foliumap as leafmap
import pandas as pd
from streamlit_folium import st_folium

# Inicializar a conexão com o Supabase
conn = st.connection("supabase", type=SupabaseConnection)

# Função para extrair as informações relevantes
def extract_relevant_info(output):
    pattern = r"Estimate generated:\s*(date.*?severity\s+\w+)"
    match = re.search(pattern, output, re.DOTALL)
    if match:
        return match.group(1)
    return None

# Função para converter a string em um dicionário
def parse_output(output):
    lines = output.strip().split('\n')
    data = {}
    for line in lines:
        key, value = line.split(None, 1)
        data[key] = value.strip()
    return data

# Função para salvar os dados no Supabase
def save_to_supabase(data):
    table = conn.table("CyFi")
    record = {
        "criado_em": datetime.datetime.now().isoformat(),
        "data": data['date'],
        "latitude": float(data['latitude']),
        "longitude": float(data['longitude']),
        "contagem": int(data['density_cells_per_ml'].replace(',', '')),
        "severidade": data['severity']
    }
    response = table.insert(record).execute()
    return response

# Função para obter dados do Supabase
@st.cache_data(ttl=600)
def get_data_from_supabase():
    table = conn.table("CyFi")
    response = table.select("*").execute()
    return response.data

# Função para criar o mapa interativo
def create_interactive_map(supabase_data):
    m = leafmap.Map(center=[-22.528801960010114, -44.5645781500265], zoom=12)
    m.add_basemap("HYBRID")

    if supabase_data:
        for row in supabase_data:
            popup = f"Data: {row['data']}<br>Contagem: {row['contagem']}<br>Severidade: {row['severidade']}"
            m.add_marker(
                location=[row['latitude'], row['longitude']],
                popup=popup,
                tooltip=f"Contagem: {row['contagem']}"
            )

    clicked_data = st_folium(m, height=600, width=700)
    coordinates = None

    if clicked_data["last_clicked"]:
        lat = clicked_data["last_clicked"]["lat"]
        lon = clicked_data["last_clicked"]["lng"]
        coordinates = (lat, lon)
        st.write(f"Coordenadas selecionadas: Latitude: {lat}, Longitude: {lon}")

    return coordinates

# Inicializar session_state
if 'coordinates' not in st.session_state:
    st.session_state.coordinates = None

# Interface principal
st.title("Previsão de Cianobactérias")

st.subheader("Mapa Interativo de Cianobactérias")
supabase_data = get_data_from_supabase()
coordinates = create_interactive_map(supabase_data)

if coordinates:
    st.session_state.coordinates = coordinates

data_selecionada = st.date_input("Selecione uma data", datetime.date.today())

if st.button("Gerar Previsão") and st.session_state.coordinates:
    latitude, longitude = st.session_state.coordinates
    data_formatada = data_selecionada.strftime("%Y-%m-%d")
    comando = f"cyfi predict-point --lat {latitude} --lon {longitude} --date {data_formatada}"

    with st.spinner("Aguarde enquanto o HidroSIS acessa as informações..."):
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)

    if resultado.returncode == 0:
        relevant_info = extract_relevant_info(resultado.stderr)
        if relevant_info:
            data = parse_output(relevant_info)
            st.success("Previsão gerada com sucesso!")
            st.table(data)

            data["latitude"] = latitude
            data["longitude"] = longitude

            try:
                save_response = save_to_supabase(data)
                if save_response.data:
                    st.success("Dados salvos com sucesso na base!")
                else:
                    st.error("Erro ao salvar dados no Supabase.")
            except Exception as e:
                st.error(f"Erro ao salvar dados no Supabase: {str(e)}")
        else:
            st.warning("Não foi possível extrair as informações relevantes da saída.")
            st.text("Saída do CyFi:")
            st.code(resultado.stderr, language="text")
    else:
        st.error("Ocorreu um erro ao executar o comando CyFi.")
        st.text("Erro:")
        st.code(resultado.stderr, language="text")