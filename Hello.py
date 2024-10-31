import streamlit as st

st.set_page_config(
    page_title="HidroSIS - Sistema de Monitoramento Hidrográfico",
    #page_icon="👋",
)

st.write("# Bem vindo ao HIDROSIS")

#st.sidebar.success("Select a demo above.")

st.markdown(
    """
    O projeto **HIDROSIS - Sistema de Monitoramento Hidrográfico** foi desenvolvido para atender às necessidades 
    dos gestores de saneamento na prevenção e controle de florações de cianobactérias no 
    Reservatório do Funil, em Resende, RJ. As cianobactérias são micro-organismos aquáticos que podem proliferar em grandes 
    quantidades, formando florações que impactam a qualidade da água e podem gerar problemas para o abastecimento e a 
    saúde pública.

    O sistema utiliza tecnologia de sensoriamento remoto para monitorar continuamente a concentração de clorofila e estimar densidade de cianobactérias 
    no reservatório. Através de satélites e outros dispositivos de coleta de dados, conseguimos obter imagens e 
    informações precisas sobre a qualidade da água, identificando rapidamente tendências de aumento dessas microalgas.
    """
    """
    **Escolha uma opção no menu lateral** para acessar as informações
    
    """
)
