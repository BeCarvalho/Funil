import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd

# Título da aplicação
st.title("Cluster de Densidade Celular no Reservatório")

# Carregar dados do arquivo CSV
url = "https://raw.githubusercontent.com/BeCarvalho/Funil/main/files/output01092023.csv"
try:
    # Especificar a codificação utf-8 para carregar caracteres especiais corretamente
    data = pd.read_csv(url, encoding="utf-8")

    # Verificar se os dados foram carregados corretamente
    if not {'latitude', 'longitude', 'density_cells_per_ml', 'severity'}.issubset(data.columns):
        st.error("O arquivo CSV não contém as colunas necessárias.")
    else:
        # Remover linhas com valores NaN nas colunas essenciais
        initial_count = len(data)
        data = data.dropna(subset=['latitude', 'longitude', 'density_cells_per_ml', 'severity'])
        final_count = len(data)

        # Informar ao usuário se linhas foram removidas
        #if final_count < initial_count:
            #st.warning(f"Linhas com dados ausentes foram removidas ({initial_count - final_count} linhas).")

        # Verificar se ainda temos dados suficientes para o mapa
        if final_count == 0:
            st.error("Não há dados suficientes para exibir o mapa após a remoção de linhas com valores ausentes.")
        else:
            # Renomear a coluna temporariamente para exibição no popup
            data = data.rename(columns={"density_cells_per_ml": "Densidade de Cianobacterias"})

            # Configuração do mapa
            st.subheader("Cluster de Densidade de Células por mL")
            map_center = [data['latitude'].mean(), data['longitude'].mean()]
            m = leafmap.Map(center=map_center, zoom=12)  # Zoom ajustado para cobrir o reservatório

            # Definir as cores em ordem para os valores de severity
            severity_colors = ["red", "yellow", "green"]  # high, moderate, low
            severity_order = ["high", "moderate", "low"]

            # Adicionar pontos como clusters com popup atualizado
            m.add_points_from_xy(
                data,
                x="longitude",
                y="latitude",
                color_column="severity",
                colors=severity_colors,  # Lista de cores em ordem
                icon_names=["circle"],
                add_legend=False,  # Remover a legenda
                popup=["latitude", "longitude", "Densidade de Cianobacterias", "severity"],  # Popups traduzidos
                categorical_column_values=severity_order,  # Ordem correspondente aos valores de severity
            )

            # Exibir o mapa
            m.to_streamlit()
except Exception as e:
    st.error(f"Ocorreu um erro ao carregar os dados: {e}")
