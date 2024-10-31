import streamlit as st

st.set_page_config(
    page_title="HidroSIS - Sistema de Monitoramento Hidrográfico",
    #page_icon="👋",
)

st.write("# Bem vindo ao HIDROSIS")

#st.sidebar.success("Select a demo above.")

st.markdown(
    """
    O projeto **HIDROSIS - Sistema de Monitoramento Hidrográfico** foi desenvolvido para atender as necessidades 
    dos gestores de saneamento na prevenção e controle de florações de cianobactérias no 
    Reservatório do Funil, em Resende. As cianobactérias são micro-organismos aquáticos que podem proliferar em grandes 
    quantidades, formando florações que impactam a qualidade da água e podem gerar problemas para o abastecimento e a 
    saúde pública.

    O sistema utiliza tecnologia de sensoriamento remoto para monitorar continuamente a densidade de cianobactérias 
    no reservatório. Através de satélites e outros dispositivos de coleta de dados, conseguimos obter imagens e 
    informações precisas sobre a qualidade da água, identificando rapidamente qualquer aumento significativo na 
    presença dessas microalgas.
    """
    """
    **Escolha uma opção no menu lateral** para acessar as informações
    ### Want to learn more?
    - Check out [streamlit.io](https://streamlit.io)
    - Jump into our [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)
    ### See more complex demos
    - Use a neural net to [analyze the Udacity Self-driving Car Image
        Dataset](https://github.com/streamlit/demo-self-driving)
    - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
    """
)