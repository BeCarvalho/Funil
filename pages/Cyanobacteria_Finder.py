import streamlit as st
import subprocess
import datetime

# Definir as coordenadas geográficas pré-definidas
LATITUDE = -22.528801960010114
LONGITUDE = -44.5645781500265

# Criar o widget de seleção de data
data_selecionada = st.date_input(
    "Selecione uma data",
    datetime.date(2023, 7, 6)
)

# Botão para gerar a previsão
if st.button("Gerar Previsão"):
    # Formatar a data para o formato esperado pelo CyFi
    data_formatada = data_selecionada.strftime("%Y-%m-%d")

    # Construir o comando CyFi com as coordenadas específicas
    comando = f"cyfi predict-point --lat {LATITUDE} --lon {LONGITUDE} --date {data_formatada}"

    # Mostrar mensagem de sucesso
    st.success("Comando gerado com sucesso!")

    # Executar o comando e capturar a saída com um spinner
    with st.spinner("Aguarde enquanto o CyFi acessa as informações..."):
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)

    # Exibir o resultado
    st.subheader("Resultado da previsão:")
    if resultado.returncode == 0:
        if resultado.stdout:
            st.code(resultado.stdout, language="text")
        else:
            st.warning("O comando foi executado com sucesso, mas não retornou nenhuma saída.")
            st.text("Comando executado:")
            st.code(comando, language="bash")
    else:
        st.error("Ocorreu um erro ao executar o comando CyFi.")
        st.text("Erro:")
        st.code(resultado.stderr, language="text")
        st.text("Comando executado:")
        st.code(comando, language="bash")

    # Exibir informações adicionais para debug
    st.subheader("Informações de Debug:")
    st.text(f"Código de retorno: {resultado.returncode}")
    st.text(f"Saída padrão (stdout):")
    st.code(resultado.stdout if resultado.stdout else "Nenhuma saída", language="text")
    st.text(f"Saída de erro (stderr):")
    st.code(resultado.stderr if resultado.stderr else "Nenhum erro", language="text")