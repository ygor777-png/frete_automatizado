import streamlit as st
import pandas as pd
import os

MOTORISTAS_FILE = "motoristas.csv"

def carregar_motoristas():
    if os.path.exists(MOTORISTAS_FILE):
        return pd.read_csv(MOTORISTAS_FILE)
    else:
        return pd.DataFrame(columns=["nome","telefone","caminhao","disponibilidade"])

def salvar_motoristas(df_motoristas):
    df_motoristas.to_csv(MOTORISTAS_FILE, index=False)

df_motoristas = carregar_motoristas()

st.title("👷 Cadastro de Motoristas")

with st.form("cadastro_motorista"):
    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone")
    caminhao = st.selectbox("Tipo de caminhão", ["Graneleiro","Rodocaçamba","Baú","Carreta"])
    disponibilidade = st.text_input("Disponibilidade (ex: SP, RJ, MG)")
    submit = st.form_submit_button("Cadastrar")

    if submit and nome and telefone:
        novo_motorista = pd.DataFrame([{
            "nome": nome,
            "telefone": telefone,
            "caminhao": caminhao,
            "disponibilidade": disponibilidade
        }])
        df_motoristas = pd.concat([df_motoristas, novo_motorista], ignore_index=True)
        salvar_motoristas(df_motoristas)
        st.success("Cadastro realizado com sucesso! ✅")
