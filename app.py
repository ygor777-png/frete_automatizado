import streamlit as st
import pandas as pd
import os
from math import ceil
from fretes import carregar_planilha, consulta_frete, mensagem_motorista, validar_rotas

# Arquivos
FRETES_FILE = "fretes.xlsx"
MOTORISTAS_FILE = "motoristas.csv"

# Funções auxiliares
def carregar_motoristas():
    if os.path.exists(MOTORISTAS_FILE) and os.path.getsize(MOTORISTAS_FILE) > 0:
        try:
            return pd.read_csv(MOTORISTAS_FILE, encoding="utf-8")
        except UnicodeDecodeError:
            return pd.read_csv(MOTORISTAS_FILE, encoding="latin1")
    else:
        return pd.DataFrame(columns=["nome","telefone","caminhao","atendimento"])

def salvar_motoristas(df_motoristas):
    df_motoristas.to_csv(MOTORISTAS_FILE, index=False, encoding="utf-8")

def salvar_fretes(df_fretes):
    df_fretes.to_excel(FRETES_FILE, index=False)

# Carregar dados
df = carregar_planilha(FRETES_FILE)
df_motoristas = carregar_motoristas()

# Sidebar para navegação
pagina = st.sidebar.selectbox("Navegação", ["Dashboard", "Fretes", "Motoristas", "Gestão de Fretes", "Frete Mínimo ANTT"])

# ---------------- Página Dashboard ----------------
if pagina == "Dashboard":
    st.title("📊 Dashboard - Automação de Fretes")

    # KPIs rápidos
    total_rotas = len(df)
    total_motoristas = len(df_motoristas)
    preco_medio_pj = df["valor_pj"].mean()
    preco_medio_pf = df["valor_pf"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rotas cadastradas", total_rotas)
    col2.metric("Motoristas cadastrados", total_motoristas)
    col3.metric("Preço médio PJ", f"R$ {preco_medio_pj:.2f}")
    col4.metric("Preço médio PF", f"R$ {preco_medio_pf:.2f}")

    # Gráfico de resumo
    resumo = df.groupby("destino")[["valor_pj","valor_pf"]].mean().reset_index()
    st.subheader("Valores médios por destino")
    st.bar_chart(resumo.set_index("destino"))

# ---------------- Página Fretes ----------------
elif pagina == "Fretes":
    st.title("🚚 Gestão de Fretes")

    st.subheader("Validação das rotas")
    st.dataframe(validar_rotas(df))

    produto = st.selectbox("Produto", ["Todos"] + list(df["produto"].unique()))
    caminhao = st.selectbox("Caminhão", ["Todos"] + list(df["caminhao"].unique()))

    df_filtrado = df.copy()
    if produto != "Todos":
        df_filtrado = df_filtrado[df_filtrado["produto"] == produto]
    if caminhao != "Todos":
        df_filtrado = df_filtrado[df_filtrado["caminhao"] == caminhao]

    origem = st.selectbox("Origem", df_filtrado["origem"].unique())
    destinos_disponiveis = df_filtrado[df_filtrado["origem"] == origem]["destino"].unique()
    destino = st.selectbox("Destino", destinos_disponiveis)
    tipo_cliente = st.radio("Tipo de cliente", ["pj","pf"])

    if st.button("Consultar frete"):
        valor = consulta_frete(df_filtrado, origem, destino, tipo_cliente)
        if valor:
            st.success(f"Frete {tipo_cliente.upper()}: R$ {valor:.2f}")
            mensagem = mensagem_motorista(df_filtrado, origem, destino, tipo_cliente)
            st.text_area("Mensagem para motorista", mensagem, height=150)
        else:
            st.error("Rota não encontrada")

    # Mensagens em lote
    if produto != "Todos":
        mensagens = []
        for _, row in df_filtrado.iterrows():
            msg = mensagem_motorista(df_filtrado, row["origem"], row["destino"], "pj")
            mensagens.append(msg)
        todas_mensagens = "\n\n".join(mensagens)

        st.text_area("Mensagens de todos os fretes filtrados", todas_mensagens, height=300)
        st.download_button("Copiar todas as mensagens", todas_mensagens, "mensagens.txt")

# ---------------- Página Motoristas ----------------
elif pagina == "Motoristas":
    st.title("👷 Cadastro de Motoristas")

    with st.form("cadastro_motorista"):
        nome = st.text_input("Nome")
        telefone = st.text_input("Telefone")
        caminhao = st.selectbox("Tipo de caminhão", ["Graneleiro","Rodocaçamba","Baú","Carreta"])
        atendimento = st.text_input("Área de atendimento (ex: SP, RJ, MG)")
        submit = st.form_submit_button("Cadastrar")

        if submit and nome and telefone:
            novo_motorista = pd.DataFrame([{
                "nome": nome,
                "telefone": telefone,
                "caminhao": caminhao,
                "atendimento": atendimento
            }])
            df_motoristas = pd.concat([df_motoristas, novo_motorista], ignore_index=True)
            salvar_motoristas(df_motoristas)
            st.success(f"Motorista {nome} cadastrado com sucesso!")

    st.subheader("Motoristas cadastrados")
    if not df_motoristas.empty:
        st.dataframe(df_motoristas)
    else:
        st.info("Nenhum motorista cadastrado ainda.")

# ---------------- Página Gestão de Fretes ----------------
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

# ---------------- Página Frete Mínimo ANTT ----------------
if pagina == "Frete Mínimo ANTT":
    st.title("🚚 Cálculo do Frete Mínimo - ANTT")

    # Inputs
    origem = st.text_input("Cidade de origem")
    destino = st.text_input("Cidade de destino")
    tonelada = st.number_input('Quantas toneladas', min_value=1.0, step=0.1)
    km = st.number_input("Distância rota 1 do Qualp (km)", min_value=1.0, step=1.0)
    eixos = st.selectbox("Quantidade de eixos do caminhão", [5, 6, 7, 9])
    pedagio_por_eixo = st.number_input("Valor do pedágio por eixo (R$)", min_value=0.0, step=0.01)
    margem = st.number_input("Margem (%)", min_value=0.0, step=0.1)
    icms = st.number_input("ICMS (%)", min_value=0.0, step=0.1)

    if st.button("Calcular frete"):
        # Fórmula simplificada (exemplo)
        # Base ANTT: custo por km varia conforme eixos, aqui vamos simular
        custo_base_por_km = {
            5: 6.0301 * km + 615.26,
            6: 6.7408 * km + 663.07,
            7: 7.313 * km + 753.88,
            9: 8.242 * km + 808.17
        }

        custo_km = custo_base_por_km[eixos]
        custo_pedagio = pedagio_por_eixo * eixos
        subtotal = custo_km + custo_pedagio
        valor_min_motorista = custo_km
        valor_min_motorista_ton = valor_min_motorista / float(tonelada)
        valor_min_fe = valor_min_motorista_ton * (1 + float(margem)/100)
        valor_motorista_com_ped = custo_pedagio + valor_min_motorista
        valor_motorista_com_ped_ton = valor_motorista_com_ped / tonelada
        valor_fe_com_ped_ton = valor_motorista_com_ped_ton * (1 + float(margem)/100)
        valor_fe_final_com_icms = valor_fe_com_ped_ton * (1 + float(icms)/100)
        

        # Aplicar margem
        valor_com_margem = subtotal * (1 + margem/100)

        # Aplicar ICMS
        valor_final = valor_com_margem * (1 + icms/100)

        mensagem = (
            f"Frete mínimo ANTT\n"
            f"Origem: {origem}\n"
            f"Destino: {destino}\n"
            f"Tonelada: {tonelada}\n"
            f"Distância: {km:.0f} km\n"
            f"Eixos: {eixos}\n"
            f"Pedágio por eixo: R$ {pedagio_por_eixo:.2f}\n"
            "\nDADOS FINAIS!\n"
            f"Valor min motorista R${valor_min_motorista:.2f}\n"
            f"Valor Ton FM R${ceil(valor_min_motorista_ton):.2f} \n"
            f"Valor Ton FE R${ceil(valor_min_fe + 1):.2f} \n"
            f"Valor min motorista com ped R${valor_motorista_com_ped:.2f}\n"
            f"Valor ton FM com ped R${ceil(valor_motorista_com_ped_ton):.2f} \n"
            f"Valor ton FE com pedagio sem ICMS R${ceil(valor_fe_com_ped_ton + 1.0):.2f} \n"
            f"valor ton FE com pedagio e ICMS R${ceil(valor_fe_final_com_icms + 1.0):.2f} \n"
        )

        st.success("✅ Cálculo realizado!")
        st.text_area("Resultado", mensagem, height=350)
        st.button("📋 Copiar resultado", on_click=lambda: st.write("Copiado!"))

    
