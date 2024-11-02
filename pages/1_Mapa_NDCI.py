import streamlit as st
import streamlit.components.v1 as components

# Configuração da página do Streamlit para melhor visualização
st.set_page_config(page_title="Monitoramento do Reservatório do Funil", layout="wide")
st.sidebar.header("Índice Médio de Clorofila")
st.sidebar.markdown("O índice Médio de Clorofila de um reservatório representa uma medida indireta de sua poluição. No mapa ao lado, selecione um intervalo de datas para obter uma média "
                    "da eutrofização observada pelo satélite em cada região do reservatório.", unsafe_allow_html=True)

# Título e introdução do app
st.title("Monitoramento do Reservatório do Funil")
st.markdown("""
    Este aplicativo exibe informações da qualidade da água do Reservatório do Funil em Resende, RJ.
    O mapa interativo abaixo é atualizado com dados do Google Earth Engine.
""")

# Exibindo o app GEE dentro do Streamlit
st.subheader("Mapa Interativo - Google Earth Engine")
gee_app_url = "https://ebenezercarvalho.users.earthengine.app/view/funil2809"

# Componente HTML para incorporar o app GEE no Streamlit
components.html(f"""
    <iframe src="{gee_app_url}" width="100%" height="700" style="border:none;"></iframe>
""", height=700)

# Rodapé ou informações adicionais (se necessário)
st.markdown("Desenvolvido por: Ebenézer Carvalho")
