import streamlit as st
import pandas as pd
from pathlib import Path
import pydeck as pdk


st.set_page_config(page_title="HIDROSIS", page_icon="📈")

st.markdown("# Densidade de Cianobactérias no Reservatório do Funil")
#st.sidebar.header("Mapa - Densidade de Cianobactérias")
#st.sidebar.markdown("Posso colocar um texto explicativo aqui se eu quiser!<br>Com uma quebra de linha.", unsafe_allow_html=True)


st.write(
    """
    Este mapa possui os valores estimados da densidade de cianobactérias no Reservatório do Funil desde 2017. Os pontos em vermelho
    correspondem às localizações no reservatório. Passe o mouse sobre cada ponto para verificar os valores
    registradas neste dia.
    
    """
)

# Carregar os dados do arquivo CSV
current_dir = Path(__file__).parent
file_path = current_dir / "output.csv"
data = pd.read_csv(file_path)

# Converter a coluna 'date' para datetime
data['date'] = pd.to_datetime(data['date'])

# Obter a lista de datas únicas
unique_dates = data['date'].dt.strftime('%d-%m-%Y').unique()

# Selecionar uma data a partir de um dropdown
selected_date = st.selectbox("Selecione uma data", unique_dates)

# Filtrar os dados pela data selecionada
filtered_data = data[data['date'].dt.strftime('%d-%m-%Y') == selected_date]

# Definir a camada do mapa (mantida igual ao exemplo original)
layer = pdk.Layer(
    'ScatterplotLayer',
    data=filtered_data,
    get_position='[lon, lat]',
    get_radius=100,
    get_fill_color='[255, 0, 0, 140]',
    pickable=True,
    auto_highlight=True,
)

# Definir a visualização do mapa (mantida igual ao exemplo original)
view_state = pdk.ViewState(
    latitude=filtered_data['lat'].mean(),
    longitude=filtered_data['lon'].mean(),
    zoom=12,
    pitch=50,
)

# Renderizar o mapa com pydeck (mantida igual ao exemplo original)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "Density: {density}"}))







#st.button("Re-run")
