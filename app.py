import streamlit as st
import pandas as pd
import os
from fretes import carregar_planilha, validar_rotas

FRETES_FILE = "fretes.xlsx"
MOTORISTAS_FILE = "motoristas.csv"

# Funções auxiliares
def carregar_motoristas():
    if os.path.exists(MOTORISTAS_FILE):
        return pd.read_csv(MOTORISTAS_FILE)
    else:
        return pd.DataFrame(columns=["nome","telefone","caminhao","disponibilidade"])

def salvar_motoristas(df_motoristas):
    df_motoristas.to_csv(MOTORISTAS_FILE, index=False)

def salvar_fretes(df_fretes):
    df_fretes.to_excel(FRETES_FILE, index=False)

# Carregar dados
df = carregar_planilha(FRETES_FILE)
df_motoristas = carregar_motoristas()

pagina = st.sidebar.selectbox("Navegação", ["Dashboard", "Fretes", "Motoristas", "Gestão de Fretes"])

# ---------------- Gestão de Fretes ----------------
if pagina == "Gestão de Fretes":
    st.title("🗂 Gestão de Fretes")

    st.subheader("Fretes atuais")
    st.dataframe(df)

    st.subheader("Adicionar novo frete")
    with st.form("novo_frete"):
        origem = st.text_input("Origem")
        destino = st.text_input("Destino")
        produto = st.text_input("Produto")
        caminhao = st.text_input("Caminhão")
        valor_pj = st.number_input("Valor PJ", min_value=0.0, step=10.0)
        valor_pf = st.number_input("Valor PF", min_value=0.0, step=10.0)
        submit = st.form_submit_button("Adicionar")

        if submit and origem and destino:
            novo = pd.DataFrame([{
                "origem": origem,
                "destino": destino,
                "produto": produto,
                "caminhao": caminhao,
                "valor_pj": valor_pj,
                "valor_pf": valor_pf
            }])
            df = pd.concat([df, novo], ignore_index=True)
            salvar_fretes(df)
            st.success("Frete adicionado com sucesso ✅")

    st.subheader("Remover frete")
    rota_remover = st.selectbox("Selecione a rota para remover", df["destino"].unique())
    if st.button("Remover frete"):
        df = df[df["destino"] != rota_remover]
        salvar_fretes(df)
        st.success(f"Frete para {rota_remover} removido com sucesso ✅")
