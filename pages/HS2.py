import streamlit as st
import subprocess
from datetime import date, datetime
import re
from st_supabase_connection import SupabaseConnection
import leafmap.foliumap as leafmap
import pandas as pd
from streamlit_folium import st_folium

# Inicializar a conexão com o Supabase
conn = st.connection("supabase", type=SupabaseConnection)

# Funções auxiliares
def extract_relevant_info(output):
    pattern = r"Estimate generated:\s*(date.*?severity\s+\w+)"
    match = re.search(pattern, output, re.DOTALL)
    return match.group(1) if match else None

def parse_output(output):
    return dict(line.split(None, 1) for line in output.strip().split('\n'))

def save_to_supabase(data):
    table = conn.table("CyFi")
    record = {
        "criado_em": datetime.now().isoformat(),
        "data": data['Data selecionada'],
        "latitude": float(data['Latitude']),
        "longitude": float(data['Longitude']),
        "contagem": int(data['Contagem']),
        "severidade": data['Intensidade']
    }
    return table.insert(record).execute()

@st.cache_data(ttl=600)
def get_data_from_supabase():
    return conn.table("CyFi").select("*").execute().data

def create_map():
    m = leafmap.Map(center=[-22.528801960010114, -44.5645781500265], zoom=13)
    m.add_basemap("HYBRID")
    return m

# Interface principal
st.title("HidroSIS - Estimativa de Cianobactérias no Reservatório do Funil")

# Inicializar estado da sessão para coordenadas
if 'coordinates' not in st.session_state:
    st.session_state.coordinates = None

# Carregar mapa inicial
m = create_map()

# Exibir mapa
st.subheader("Clique em uma região do reservatório para gerar as contagens.")
with st.container():
    map_data = st_folium(m, width=700, height=500)

    # Processar clique no mapa
    if map_data and map_data.get("last_clicked"):
        lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
        st.session_state.coordinates = (lat, lon)

    if st.session_state.coordinates:
        lat, lon = st.session_state.coordinates
        col1, col2 = st.columns(2)
        col1.metric("Latitude", f"{lat:.6f}")
        col2.metric("Longitude", f"{lon:.6f}")

# Interface de previsão
data_selecionada = st.date_input("Selecione uma data:", date.today())

# Botão para gerar previsão
if st.button("Gerar Previsão") and st.session_state.coordinates:
    lat, lon = st.session_state.coordinates
    data_formatada = data_selecionada.strftime("%Y-%m-%d")
    comando = f"cyfi predict-point --lat {lat} --lon {lon} --date {data_formatada}"

    with st.spinner("Gerando previsão..."):
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)

    if resultado.returncode == 0:
        info = extract_relevant_info(resultado.stderr)
        if info:
            data = parse_output(info)
            severidade_map = {"high": "alta", "moderate": "média", "low": "baixa"}
            intensidade = severidade_map.get(data['severity'], data['severity'])
            contagem = int(data['density_cells_per_ml'].replace(',', '')) if isinstance(data['density_cells_per_ml'], str) else data['density_cells_per_ml']

            df_formatado = pd.DataFrame({
                "Informação": ["Data", "Latitude", "Longitude", "Contagem", "Intensidade"],
                "Valor": [
                    datetime.strptime(data['date'], "%Y-%m-%d").strftime("%d-%m-%Y"),
                    f"{float(data['latitude']):.6f}",
                    f"{float(data['longitude']):.6f}",
                    f"{contagem:,}",
                    intensidade
                ]
            })
            st.success("Previsão gerada com sucesso!")
            st.table(df_formatado)

            # Preparar dados para salvar no Supabase
            dados_para_salvar = {
                "Data selecionada": data['date'],  # Mantém o formato original YYYY-MM-DD
                "Latitude": float(data['latitude']),
                "Longitude": float(data['longitude']),
                "Contagem": contagem,
                "Intensidade": intensidade
            }

            try:
                save_to_supabase(dados_para_salvar)
                st.success("Dados salvos com sucesso na base!")
            except Exception as e:
                st.error(f"Erro ao salvar dados: {str(e)}")
        else:
            st.warning("Não foi possível extrair as informações relevantes.")
    else:
        st.error("Erro ao executar o comando CyFi.")
        st.code(resultado.stderr, language="text")

# Obter dados do Supabase
supabase_data = get_data_from_supabase()

# Exibir dados do Supabase com filtro de mês e ano
st.subheader("Dados da Base")

# Seletor de mês e ano
with st.container():
    col1, col2 = st.columns(2)
    mes = col1.selectbox("Selecione o mês:", range(1, 13), format_func=lambda x: datetime(1900, x, 1).strftime("%B"))
    ano = col2.selectbox("Selecione o ano:", range(datetime.now().year, datetime.now().year - 10, -1))

# Filtrar dados
if supabase_data:
    df = pd.DataFrame(supabase_data)
    df['data'] = pd.to_datetime(df['data'])
    df_filtrado = df[(df['data'].dt.month == mes) & (df['data'].dt.year == ano)]

    if not df_filtrado.empty:
        st.dataframe(df_filtrado)
    else:
        st.warning("Não há dados disponíveis para o período selecionado. Por favor, escolha outro período.")
else:
    st.warning("Não há dados disponíveis na base.")
