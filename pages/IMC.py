import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# Configuração do Supabase
supabase_url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
supabase_key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)


# Função para salvar dados no Supabase
def save_to_supabase(idade, peso, altura, imc, classificacao):
    data = supabase.table("imc_results").insert({
        "idade": idade,
        "peso": peso,
        "altura": altura,
        "imc": imc,
        "classificacao": classificacao
    }).execute()
    return data


# Função para carregar dados do Supabase
@st.cache_data(ttl=10)
def load_data():
    data = supabase.table("imc_results").select("*").order('timestamp', desc=True).limit(100).execute()
    return pd.DataFrame(data.data)


# Título do aplicativo
st.title("Calculadora de IMC")

# Entrada de dados do usuário
idade = st.number_input("Digite sua idade", min_value=0, max_value=120, step=1)
peso = st.number_input("Digite seu peso (kg)", min_value=0.0, step=0.1)
altura = st.number_input("Digite sua altura (m)", min_value=0.0, max_value=3.0, step=0.01)

# Botão azul para calcular o IMC
with stylable_container(
        key="blue_button",
        css_styles="""
        button {
            background-color: blue;
            color: white;
        }
    """
):
    if st.button("Calcular IMC"):
        # Cálculo do IMC
        imc = peso / (altura ** 2)

        # Classificação do IMC
        if imc < 18.5:
            classificacao = "Abaixo do peso"
        elif 18.5 <= imc < 24.9:
            classificacao = "Peso normal"
        elif 25 <= imc < 29.9:
            classificacao = "Sobrepeso"
        else:
            classificacao = "Obeso"

        # Exibição do resultado
        st.write(f"Seu IMC é: {imc:.2f}")
        st.write(f"Classificação: {classificacao}")
        st.write(f"Idade informada: {idade} anos")

        # Salvar dados no Supabase
        save_to_supabase(idade, peso, altura, round(imc, 2), classificacao)
        st.success("Dados salvos com sucesso!")

# Exibir tabela com resultados
st.subheader("Resultados Anteriores")
df = load_data()
st.dataframe(df)

# Criar e exibir o histograma
st.subheader("Distribuição dos últimos 100 valores de IMC")
fig = px.histogram(df, x="imc", nbins=20, title="Histograma de IMC")
fig.update_layout(bargap=0.1)
st.plotly_chart(fig, use_container_width=True)