# Lê a planilha de Excel (arquivo ou buffer de upload) e organiza os dados
import pandas as pd
import io


def eh_excel(fonte_ou_nome):
    if isinstance(fonte_ou_nome, str):
        nome = fonte_ou_nome.lower()
        return nome.endswith(".xlsx") or nome.endswith(".xls")
    if hasattr(fonte_ou_nome, "name"):
        nome = fonte_ou_nome.name.lower()
        return nome.endswith(".xlsx") or nome.endswith(".xls")
    return True


def detectar_tipo(colunas):
    nomes = [str(c).strip().upper() for c in colunas]
    if any("DATA" in n for n in nomes) and "TOTAL" in nomes:
        return "periodo"
    if "CODIGO" in nomes and "DESCRICAO" in nomes:
        return "produtos"
    return None


def virar_numero(valor):
    try:
        return float(valor)
    except Exception:
        return 0.0


def ler_periodo(tabela):
    tabela.columns = [str(c).strip().upper() for c in tabela.columns]
    col_data = [c for c in tabela.columns if "DATA" in c][0] if any("DATA" in c for c in tabela.columns) else "DATA INICIAL"
    
    linhas = []
    for _, linha in tabela.iterrows():
        data = pd.to_datetime(linha[col_data], errors="coerce")
        if pd.isna(data):
            continue
        linhas.append({
            "data_inicial": data.date(),
            "mes": data.month,
            "ano": data.year,
            "total": round(virar_numero(linha["TOTAL"]), 2),
        })
    return linhas


def ler_produtos(tabela):
    tabela.columns = [str(c).strip().upper() for c in tabela.columns]
    linhas = []
    for _, linha in tabela.iterrows():
        nome = linha["DESCRICAO"]
        if pd.isna(nome):
            continue
        nome = " ".join(str(nome).split())
        linhas.append({
            "codigo": int(virar_numero(linha.get("CODIGO", 0))),
            "descricao": nome,
            "quantidade": round(virar_numero(linha.get("QUANTIDADE", 0)), 2),
            "total": round(virar_numero(linha.get("TOTAL", 0)), 2),
            "lucro": round(virar_numero(linha.get("LUCRO", 0)), 2),
        })
    return linhas


def processar(fonte):
    if not eh_excel(fonte):
        return None, []

    try:
        if isinstance(fonte, bytes):
            tabela = pd.read_excel(io.BytesIO(fonte))
        elif hasattr(fonte, "read"):
            # garante ponteiro no inicio antes e depois da leitura
            if hasattr(fonte, "seek"):
                fonte.seek(0)
            conteudo = fonte.read()
            if hasattr(fonte, "seek"):
                fonte.seek(0)
            tabela = pd.read_excel(io.BytesIO(conteudo))
        else:
            tabela = pd.read_excel(fonte)
    except Exception:
        return None, []

    tipo = detectar_tipo(tabela.columns)
    if tipo == "periodo":
        return tipo, ler_periodo(tabela)
    if tipo == "produtos":
        return tipo, ler_produtos(tabela)
    return None, []
