import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
from st_supabase_connection import SupabaseConnection

# Inicializa a conexão com o Supabase
conn = st.connection("supabase", type=SupabaseConnection)

# Consulta a tabela CyFi
query = "SELECT * FROM CyFi"
rows = conn.client.table("CyFi").select("*").execute()

# Converte os resultados para um DataFrame
df = pd.DataFrame(rows.data)

# Cria um mapa centrado na média das coordenadas
m = leafmap.Map(center=[df['latitude'].mean(), df['longitude'].mean()], zoom=12)

# Adiciona o mapa de calor
m.add_heatmap(
    df,
    latitude="latitude",
    longitude="longitude",
    value="contagem",
    name="Mapa de Calor",
    radius=25,
)

# Exibe o mapa no Streamlit
st.title("HidroSIS - Mapa de Calor")
m.to_streamlit(height=700)

# Exibe os dados em uma tabela (opcional)
st.subheader("hIDROsis - Dados")
st.dataframe(df)
