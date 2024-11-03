import streamlit as st
import subprocess
import datetime
import re
from st_supabase_connection import SupabaseConnection

# Definir as coordenadas geográficas pré-definidas
LATITUDE = -22.528801960010114
LONGITUDE = -44.5645781500265

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


# Criar o widget de seleção de data
data_selecionada = st.date_input(
    "Selecione uma data",
    datetime.date(2023, 7, 6)
)

# Botão para gerar a previsão
if st.button("Gerar Previsão"):
    data_formatada = data_selecionada.strftime("%Y-%m-%d")
    comando = f"cyfi predict-point --lat {LATITUDE} --lon {LONGITUDE} --date {data_formatada}"

    with st.spinner("Aguarde enquanto o CyFi acessa as informações..."):
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)

    if resultado.returncode == 0:
        relevant_info = extract_relevant_info(resultado.stderr)
        if relevant_info:
            data = parse_output(relevant_info)
            st.success("Previsão gerada com sucesso!")
            st.table(data)

            # Salvar dados no Supabase
            try:
                save_response = save_to_supabase(data)
                if save_response.data:
                    st.success("Dados salvos com sucesso no Supabase!")
                else:
                    st.error("Erro ao salvar dados no Supabase.")
            except Exception as e:
                st.error(f"Erro ao salvar dados no Supabase: {str(e)}")
        else:
            st.warning("Não foi possível extrair as informações relevantes da saída.")
    else:
        st.error("Ocorreu um erro ao executar o comando CyFi.")
        st.text("Erro:")
        st.code(resultado.stderr, language="text")