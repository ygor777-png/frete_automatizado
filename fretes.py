import pandas as pd
import unicodedata

# Função para normalizar textos (remove acentos, coloca em minúsculo)
def normaliza(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
    return texto

def carregar_planilha(caminho="fretes.xlsx"):
    df = pd.read_excel(caminho, engine="openpyxl")
    for col in ["origem","destino","caminhao","produto"]:
        df[col] = df[col].apply(normaliza)
    return df

def valida_regra(row):
    prod = row["produto"]
    cam = row["caminhao"]
    if prod in ["calcario","gesso"] and cam != "rodocacamba":
        return "Erro: produto exige rodocaçamba"
    if prod == "adubo" and cam != "graneleiro":
        return "Erro: adubo exige graneleiro"
    return "OK"

def validar_rotas(df):
    df["validacao"] = df.apply(valida_regra, axis=1)
    return df[["origem","destino","produto","caminhao","validacao"]]

def consulta_frete(df, origem, destino, tipo_cliente="pj"):
    origem = normaliza(origem)
    destino = normaliza(destino)
    filtro = df[(df["origem"]==origem) & (df["destino"]==destino)]
    if filtro.empty:
        return None
    return float(filtro.iloc[0][f"valor_{tipo_cliente.lower()}"])

def mensagem_motorista(df, origem, destino, tipo_cliente="pj"):
    origem = normaliza(origem)
    destino = normaliza(destino)
    filtro = df[(df["origem"]==origem) & (df["destino"]==destino)]
    if filtro.empty:
        return "Rota não encontrada"
    rota = filtro.iloc[0]
    valor = rota[f"valor_{tipo_cliente.lower()}"]
    return (f"Carga disponível!\n"
            f"Produto: {rota['produto']}\n"
            f"Origem: {rota['carregamento']} ({origem})\n"
            f"Destino: {rota['descarga']} ({destino})\n"
            f"Caminhão: {rota['caminhao']}\n"
            f"Frete {tipo_cliente.upper()}: R$ {valor:.2f}")

if __name__ == "__main__":
    df = carregar_planilha("fretes.xlsx")
    print("Validação das rotas:")
    print(validar_rotas(df))

    print("\nConsulta de frete Catanduva PF:")
    print(consulta_frete(df,"santana de parnaiba","catanduva","pf"))

    print("\nMensagem para motorista Meridiano PJ:")
    print(mensagem_motorista(df,"santana de parnaiba","meridiano","pj"))

    
