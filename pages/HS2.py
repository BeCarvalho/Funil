import streamlit as st
import subprocess
from datetime import date, datetime
import re
from st_supabase_connection import SupabaseConnection
import pandas as pd
import folium
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
        "latitude": data['Latitude'],
        "longitude": data['Longitude'],
        "contagem": data['Contagem'],
        "severidade": data['Intensidade']
    }
    return table.insert(record).execute()

@st.cache_data(ttl=600)
def get_data_from_supabase():
    return conn.table("CyFi").select("data", "latitude", "longitude", "contagem", "severidade").execute().data

# Interface principal
st.title("HidroSIS - Estimativa de Cianobactérias no Reservatório do Funil")

# Criar o mapa
m = folium.Map(location=[-22.529560224597578, -44.56332013747647], zoom_start=10)

# Adicionar marcadores existentes ao mapa
supabase_data = get_data_from_supabase()
if supabase_data:
    df = pd.DataFrame(supabase_data)
    for idx, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"Data: {row['data']}<br>Contagem: {row['contagem']}<br>Intensidade: {row['severidade']}",
            tooltip=f"Contagem: {row['contagem']}"
        ).add_to(m)

# Exibir o mapa e capturar eventos de clique
map_data = st_folium(m, width=700, height=500)

# Inicializar variáveis para latitude e longitude
latitude = -22.529560224597578
longitude = -44.56332013747647

# Verificar se um ponto foi selecionado no mapa
if map_data['last_clicked'] is not None:
    latitude = map_data['last_clicked']['lat']
    longitude = map_data['last_clicked']['lng']
    st.write(f"Coordenadas selecionadas: Latitude {latitude:.6f}, Longitude {longitude:.6f}")

# Interface de previsão
data_selecionada = st.date_input("Selecione uma data:", date.today())

if st.button("Gerar Previsão"):
    data_formatada = data_selecionada.strftime("%Y-%m-%d")
    comando = f"cyfi predict-point --lat {latitude} --lon {longitude} --date {data_formatada}"

    with st.spinner("Gerando previsão..."):
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)

    if resultado.returncode == 0:
        info = extract_relevant_info(resultado.stderr)
        if info:
            data = parse_output(info)
            severidade_map = {"high": "alta", "moderate": "média", "low": "baixa"}
            intensidade = severidade_map.get(data['severity'], data['severity'])
            contagem = int(data['density_cells_per_ml'].replace(',', ''))

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
                "Data selecionada": data['date'],
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

# Exibir dados do Supabase
st.subheader("Dados da Base")
if supabase_data:
    st.dataframe(df)
else:
    st.warning("Não há dados disponíveis na base.")