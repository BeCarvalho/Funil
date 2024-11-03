import streamlit as st
import subprocess
import datetime
from datetime import date, datetime
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
        "criado_em": datetime.now().isoformat(),
        "data": data['Data selecionada'],
        "latitude": float(data['Latitude']),
        "longitude": float(data['Longitude']),
        "contagem": int(data['Contagem'].replace(',', '')),
        "severidade": data['Intensidade']
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
    # Definindo uma largura maior para o mapa
    map_width = 1000  # Você pode ajustar este valor conforme necessário

    m = leafmap.Map(center=[-22.528801960010114, -44.5645781500265], zoom=13)
    m.add_basemap("HYBRID")

    if supabase_data:
        for row in supabase_data:
            popup = f"Data: {row['data']}<br>Contagem: {row['contagem']}<br>Severidade: {row['severidade']}"
            m.add_marker(
                location=[row['latitude'], row['longitude']],
                popup=popup,
                tooltip=f"Contagem: {row['contagem']}"
            )

    # Usando st_folium com largura específica e altura proporcional
    clicked_data = st_folium(m, width=map_width, height=map_width * 0.6)

    coordinates = None
    if clicked_data["last_clicked"]:
        lat = clicked_data["last_clicked"]["lat"]
        lon = clicked_data["last_clicked"]["lng"]
        coordinates = (lat, lon)

        # Criando um container para as coordenadas
        with st.container():
            st.markdown("<h3 style='text-align: center;'><strong>Coordenadas selecionadas</strong></h3>",
                        unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Latitude", value=f"{lat:.6f}")
            with col2:
                st.metric(label="Longitude", value=f"{lon:.6f}")

    return coordinates

# Inicializar session_state
if 'coordinates' not in st.session_state:
    st.session_state.coordinates = None

# Interface principal
st.title("HidroSIS - Estimativa de Cianobactérias no Reservatório do Funil")

st.subheader("Clique em uma região do reservatório para gerar as contagens.")
supabase_data = get_data_from_supabase()
coordinates = create_interactive_map(supabase_data)

if coordinates:
    st.session_state.coordinates = coordinates

data_selecionada = st.date_input("Agora, selecione uma data:", date.today())

if st.button("Gerar Previsão") and st.session_state.coordinates:
    latitude, longitude = st.session_state.coordinates
    data_formatada = data_selecionada.strftime("%Y-%m-%d")
    comando = f"cyfi predict-point --lat {latitude} --lon {longitude} --date {data_formatada}"

    with st.spinner("Aguarde enquanto o HidroSIS acessa as informações. Isso pode levar algum tempo."):
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)

    if resultado.returncode == 0:
        relevant_info = extract_relevant_info(resultado.stderr)
        if relevant_info:
            data = parse_output(relevant_info)

            # Tradução e formatação dos dados
            data_formatada = datetime.strptime(data['date'], "%Y-%m-%d").strftime("%d-%m-%Y")
            contagem = int(data['density_cells_per_ml'].replace(',', ''))

            # Tradução da severidade
            severidade_map = {"high": "alta", "moderate": "média", "low": "baixa"}
            intensidade = severidade_map.get(data['severity'], data['severity'])

            # Criando um DataFrame formatado
            df_formatado = pd.DataFrame({
                "Informação": ["Data selecionada", "Latitude", "Longitude", "Contagem", "Intensidade"],
                "Valor": [data_formatada, f"{float(data['latitude']):.6f}", f"{float(data['longitude']):.6f}",
                          f"{contagem:,}", intensidade]
            })

            st.success("Previsão gerada com sucesso!")
            st.table(df_formatado)

            # Preparando os dados para salvar no Supabase
            dados_para_salvar = {
                "Data selecionada": data['date'],  # Mantém o formato original YYYY-MM-DD para o banco de dados
                "Latitude": data['latitude'],
                "Longitude": data['longitude'],
                "Contagem": data['density_cells_per_ml'],
                "Intensidade": intensidade
            }

            try:
                save_response = save_to_supabase(dados_para_salvar)
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

# Exibir tabela com dados do Supabase
st.subheader("Dados da Base")
if supabase_data:
    df = pd.DataFrame(supabase_data)
    st.dataframe(df)
else:
    st.warning("Não há dados disponíveis na base.")