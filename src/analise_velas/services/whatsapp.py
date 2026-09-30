# Monta o resumo de vendas para enviar pelo WhatsApp
from urllib.parse import quote
from sqlalchemy import func
from analise_velas.database import Importacao, VendaMensal
from analise_velas.services.analise import analisar_produtos, reais
from analise_velas.services.calendario import MESES


def quantidade_br(valor):
    # 150.0 -> "150" e 12.5 -> "12,50" (padrão brasileiro)
    if valor == int(valor):
        return "{:,}".format(int(valor)).replace(",", ".")
    texto = "{:,.2f}".format(valor)
    return texto.replace(",", "#").replace(".", ",").replace("#", ".")


def gerar_resumo_whatsapp(db):
    # o "mês atual" é o mês mais recente que existe nas planilhas de vendas mensais
    ultimo = (
        db.query(VendaMensal.ano, VendaMensal.mes)
        .filter(VendaMensal.ano.isnot(None))
        .order_by(VendaMensal.ano.desc(), VendaMensal.mes.desc())
        .first()
    )

    # a planilha de produtos não tem data, então usa a última que foi enviada
    ultima_prod = (
        db.query(Importacao.id)
        .filter(Importacao.tipo_planilha == "produtos")
        .order_by(Importacao.id.desc())
        .first()
    )

    if ultimo is None and ultima_prod is None:
        return None

    linhas = ["*Resumo de Vendas - Velas SC*"]

    if ultimo is not None:
        ano, mes = ultimo
        total_mes = db.query(func.sum(VendaMensal.total)).filter(
            VendaMensal.ano == ano, VendaMensal.mes == mes
        ).scalar() or 0.0
        total_ano = db.query(func.sum(VendaMensal.total)).filter(
            VendaMensal.ano == ano
        ).scalar() or 0.0

        linhas.append(f"Mês: {MESES[mes]}/{ano}")
        linhas.append("")
        linhas.append(f"Faturamento do mês: {reais(total_mes)}")
        linhas.append(f"Faturamento acumulado no ano: {reais(total_ano)}")

    if ultima_prod is not None:
        analise = analisar_produtos(db, importacao_ids=ultima_prod.id)
        if analise:
            # o ranking é pelo faturamento (R$), porque kg e unidade não podem ser somados
            linhas.append("")
            linhas.append("*Produtos mais vendidos:*")
            for i, p in enumerate(analise["ranking"][:5], start=1):
                linhas.append(f"{i}. {p['descricao']} - {quantidade_br(p['quantidade'])} {p['unidade']}")

    return "\n".join(linhas)


def link_whatsapp(texto):
    # codifica o texto para a URL: quebras de linha viram %0A e acentos também são convertidos.
    # o texto não usa emojis porque o link wa.me troca os emojis por "�" ao abrir o WhatsApp
    return "https://wa.me/?text=" + quote(texto, safe="")
