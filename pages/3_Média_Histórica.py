import streamlit as st
import pandas as pd
from pathlib import Path
#import pydeck as pdk
import altair as alt  # Biblioteca para gráficos interativos

# Carregar os dados do arquivo CSV
current_dir = Path(__file__).parent
file_path = current_dir / "output.csv"
data = pd.read_csv(file_path)

# Converter a coluna 'date' para datetime
data['date'] = pd.to_datetime(data['date'])

# Obter a lista de datas únicas
unique_dates = data['date'].dt.strftime('%d-%m-%Y').unique()

# Agora vamos plotar um gráfico das médias de densidade por mês
data['month'] = data['date'].dt.to_period('M')
avg_density_data = data.groupby('month')['density'].mean().reset_index()
avg_density_data['month'] = avg_density_data['month'].dt.to_timestamp()

# Plotar o gráfico de barras utilizando Altair

st.write("### Médias Mensais de Densidade")

chart = alt.Chart(avg_density_data).mark_bar().encode(
    x=alt.X('month:T', title='Mês'),
    y=alt.Y('density:Q', title='Densidade Média'),
    tooltip=['month:T', 'density:Q']
).properties(
    width='container',
    height=400,


    ).interactive()
st.altair_chart(chart, use_container_width=True)  # Permite que o gráfico use a largura total da coluna


st.altair_chart(chart)