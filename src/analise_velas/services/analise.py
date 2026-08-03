# Faz as contas das vendas (periodo e produtos)
from analise_velas.database import VendaMensal, VendaProduto, Produto
from analise_velas.services.calendario import datas_do_mes, MESES


def reais(valor):
    # Formata numero para R$ no padrao brasileiro
    texto = "{:,.2f}".format(valor)
    texto = texto.replace(",", "#").replace(".", ",").replace("#", ".")
    return "R$ " + texto


def filtrar_por_importacao(query, coluna, importacao_ids):
    # deixa passar tudo se nao houver filtro, senao aceita um id unico ou uma lista de ids
    if importacao_ids is None:
        return query
    if isinstance(importacao_ids, list):
        return query.filter(coluna.in_(importacao_ids)) if importacao_ids else None
    return query.filter(coluna == importacao_ids)


def analisar_periodo(db, importacao_ids=None):
    query = filtrar_por_importacao(db.query(VendaMensal), VendaMensal.importacao_id, importacao_ids)
    if query is None:
        return None

    vendas = query.order_by(VendaMensal.mes).all()
    if not vendas:
        return None

    # Agrupa por mes para consolidar caso haja mais de uma planilha de periodo
    vendas_por_mes = {}
    for v in vendas:
        m = v.mes
        a = v.ano or 2026
        chave = (m, a)
        if chave not in vendas_por_mes:
            vendas_por_mes[chave] = {"mes": m, "ano": a, "total": 0.0}
        vendas_por_mes[chave]["total"] += float(v.total)

    lista_agrupada = list(vendas_por_mes.values())
    lista_agrupada.sort(key=lambda x: x["mes"])

    total = sum(item["total"] for item in lista_agrupada)
    pico = max(lista_agrupada, key=lambda x: x["total"])
    fraco = min(lista_agrupada, key=lambda x: x["total"])

    periodos = []
    anterior = None
    for item in lista_agrupada:
        val = item["total"]
        if anterior and anterior > 0:
            variacao = round((val - anterior) / anterior * 100, 1)
        else:
            variacao = None

        datas = [d["nome"] for d in datas_do_mes(item["mes"], item["ano"])]
        periodos.append({
            "mes_num": item["mes"],
            "nome": MESES[item["mes"]],
            "total": round(val, 2),
            "variacao_pct": variacao,
            "datas": datas,
        })
        anterior = val

    destaque = f"Maior faturamento registrado no mês de {MESES[pico['mes']]} ({reais(pico['total'])})."
    for d in datas_do_mes(pico["mes"], pico["ano"]):
        if d["forte"]:
            destaque += f" Período coincidente com {d['nome']}."
            break


    return {
        "tipo": "periodo",
        "resumo": {
            "total_periodo": round(total, 2),
            "media": round(total / len(lista_agrupada), 2),
            "pico": {"nome": MESES[pico["mes"]], "total": pico["total"]},
            "fraco": {"nome": MESES[fraco["mes"]], "total": fraco["total"]},
        },
        "periodos": periodos,
        "destaque": destaque,
    }


def analisar_produtos(db, importacao_ids=None):
    query = db.query(VendaProduto, Produto).join(Produto)
    query = filtrar_por_importacao(query, VendaProduto.importacao_id, importacao_ids)
    if query is None:
        return None

    linhas = query.all()
    if not linhas:
        return None

    # Agrupa por produto para consolidar caso haja mais de uma planilha de produtos
    produtos_map = {}
    faturamento_total = 0.0
    lucro_total = 0.0

    for venda, produto in linhas:
        desc = produto.descricao
        faturamento_total += float(venda.total)
        lucro_total += float(venda.lucro)
        
        if desc not in produtos_map:
            unidade = "kg" if "KG" in desc.upper() else "un"
            produtos_map[desc] = {
                "descricao": desc,
                "codigo": produto.codigo,
                "unidade": unidade,
                "quantidade": 0.0,
                "total": 0.0,
                "lucro": 0.0,
            }
        
        produtos_map[desc]["quantidade"] += float(venda.quantidade)
        produtos_map[desc]["total"] += float(venda.total)
        produtos_map[desc]["lucro"] += float(venda.lucro)

    ranking = []
    for desc, item in produtos_map.items():
        tot = item["total"]
        luc = item["lucro"]
        part = round(tot / faturamento_total * 100, 1) if faturamento_total > 0 else 0.0
        marg = round(luc / tot * 100, 1) if tot > 0 else 0.0
        
        ranking.append({
            "descricao": desc,
            "quantidade": round(item["quantidade"], 2),
            "unidade": item["unidade"],
            "total": round(tot, 2),
            "lucro": round(luc, 2),
            "participacao_pct": part,
            "margem_pct": marg,
        })

    ranking.sort(key=lambda p: p["total"], reverse=True)

    margem_geral = round(lucro_total / faturamento_total * 100, 1) if faturamento_total > 0 else 0.0

    return {
        "tipo": "produtos",
        "resumo": {
            "faturamento_total": round(faturamento_total, 2),
            "lucro_total": round(lucro_total, 2),
            "margem_geral_pct": margem_geral,
            "qtd_produtos": len(ranking),
        },
        "ranking": ranking,
    }
