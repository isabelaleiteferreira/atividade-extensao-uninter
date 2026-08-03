# Aplicacao Streamlit para Analise de Vendas de Velas (TCC CST Banco de Dados)
import streamlit as st
import pandas as pd

from analise_velas.database import (
    criar_tabelas, SessionLocal,
    Importacao, VendaMensal, Produto, VendaProduto
)
from analise_velas.services.leitura import processar
from analise_velas.services.analise import analisar_periodo, analisar_produtos, reais

st.set_page_config(page_title="Analise de Vendas - Fabrica de Velas", layout="wide")

# aumenta o tamanho da fonte em toda a pagina para facilitar a leitura
st.markdown("""
<style>
html, body, [class*="css"] { font-size: 19px; }
h1 { font-size: 2.4rem !important; }
h2 { font-size: 1.9rem !important; }
h3 { font-size: 1.5rem !important; }
[data-testid="stMetricValue"] { font-size: 1.8rem !important; }
[data-testid="stMetricLabel"] { font-size: 1.05rem !important; }
</style>
""", unsafe_allow_html=True)


# roda so uma vez por sessao do servidor, nao a cada interacao
@st.cache_resource(show_spinner="Conectando ao banco de dados...")
def iniciar_banco():
    try:
        criar_tabelas()
    except Exception:
        pass

iniciar_banco()


# evita salvar o mesmo arquivo duas vezes ao recarregar a pagina
if "arquivos_processados" not in st.session_state:
    st.session_state["arquivos_processados"] = set()


def criar_importacao(db, nome, tipo, total_linhas):
    imp = Importacao(nome_arquivo=nome, tipo_planilha=tipo, total_registros=total_linhas)
    db.add(imp)
    db.flush()
    return imp


def salvar_periodo(db, nome, tipo, linhas):
    try:
        imp = criar_importacao(db, nome, tipo, len(linhas))
        for l in linhas:
            db.add(VendaMensal(
                importacao_id=imp.id,
                data_inicial=l["data_inicial"],
                mes=l["mes"],
                ano=l["ano"],
                total=l["total"]
            ))
        db.commit()
    except Exception:
        db.rollback()
        raise


def salvar_produtos(db, nome, tipo, linhas):
    try:
        imp = criar_importacao(db, nome, tipo, len(linhas))
        produtos_existentes = {p.descricao: p for p in db.query(Produto).all()}

        for l in linhas:
            nome_prod = l["descricao"]
            if nome_prod in produtos_existentes:
                prod = produtos_existentes[nome_prod]
            else:
                prod = Produto(codigo=l["codigo"], descricao=nome_prod)
                db.add(prod)
                db.flush()
                produtos_existentes[nome_prod] = prod

            db.add(VendaProduto(
                importacao_id=imp.id,
                produto_id=prod.id,
                quantidade=l["quantidade"],
                total=l["total"],
                lucro=l["lucro"]
            ))
        db.commit()
    except Exception:
        db.rollback()
        raise


# --- BARRA LATERAL (PAINEL DE CONTROLE) ---
st.sidebar.title("Fabrica de Velas")
st.sidebar.caption("Banco de Dados: Supabase (PostgreSQL)")
st.sidebar.markdown("---")

st.sidebar.subheader("1. Carregar Planilhas")
st.sidebar.write("Arraste ou selecione uma ou mais planilhas Excel (.xlsx). O sistema identifica automaticamente se o arquivo e de vendas mensais ou de produtos.")

arquivos_enviados = st.sidebar.file_uploader(
    "Selecione arquivos (.xlsx ou .xls):",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

if arquivos_enviados:
    novos = 0
    try:
        with SessionLocal() as db_upload, st.spinner("Salvando planilhas no banco de dados..."):
            for arq in arquivos_enviados:
                chave = f"{arq.name}_{arq.size}"
                if chave not in st.session_state["arquivos_processados"]:
                    tipo, linhas = processar(arq)
                    if tipo and linhas:
                        if tipo == "periodo":
                            salvar_periodo(db_upload, arq.name, tipo, linhas)
                        elif tipo == "produtos":
                            salvar_produtos(db_upload, arq.name, tipo, linhas)
                        st.session_state["arquivos_processados"].add(chave)
                        novos += 1
    except Exception:
        st.sidebar.error("Nao foi possivel registrar o arquivo. Verifique a conexao com o banco de dados.")

    if novos > 0:
        st.sidebar.success(f"{novos} nova(s) planilha(s) cadastrada(s) com sucesso. Atualize a pagina (tecla F5) para ver os dados no painel.")

st.sidebar.markdown("---")
st.sidebar.subheader("2. Opcoes de Visualizacao")

# o "with" garante que a conexao e fechada mesmo se a pagina for interrompida
with SessionLocal() as db:
    analise_per = None
    analise_prod = None
    titulo_origem = "Visao Consolidada de Todos os Registros"

    with st.spinner("Carregando dados do banco..."):
        historico_opcoes = {"Visao Consolidada (Todas as Planilhas)": "TODAS"}
        try:
            importacoes = db.query(Importacao).order_by(Importacao.id.desc()).all()
            for imp in importacoes:
                data_fmt = imp.data_importacao.strftime("%d/%m/%Y %H:%M") if imp.data_importacao else ""
                historico_opcoes[f"ID #{imp.id} - {imp.nome_arquivo} ({imp.tipo_planilha.upper()}) - {data_fmt}"] = imp.id
        except Exception:
            pass

    selecao = st.sidebar.selectbox("Escolha os dados a exibir:", options=list(historico_opcoes.keys()))
    filtro_id = historico_opcoes[selecao]

    with st.spinner("Calculando analise..."):
        try:
            if filtro_id == "TODAS":
                analise_per = analisar_periodo(db, importacao_ids=None)
                analise_prod = analisar_produtos(db, importacao_ids=None)
                titulo_origem = "Visao Consolidada de Todos os Registros"
            else:
                imp_sel = db.query(Importacao).filter(Importacao.id == filtro_id).first()
                if imp_sel:
                    if imp_sel.tipo_planilha == "periodo":
                        analise_per = analisar_periodo(db, importacao_ids=filtro_id)
                        titulo_origem = f"{imp_sel.nome_arquivo} (Vendas Mensais)"
                    else:
                        analise_prod = analisar_produtos(db, importacao_ids=filtro_id)
                        titulo_origem = f"{imp_sel.nome_arquivo} (Analise de Produtos)"
        except Exception:
            st.error("Erro ao carregar dados do banco de dados. Tente atualizar a pagina.")


# --- PAINEL PRINCIPAL ---
st.title("Painel de Inteligencia de Vendas - Fabrica de Velas")
st.write("Analise simplificada de faturamento, desempenho de produtos e relacao com datas religiosas e feriados.")
st.caption(f"Visualizando: {titulo_origem}")
st.markdown("---")

if analise_per is None and analise_prod is None:
    st.info("Envie suas planilhas de vendas pela barra lateral, a esquerda, para comecar.")

    st.markdown("### O que voce vai descobrir:")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("#### Quanto a fabrica faturou")
        st.write("Veja o total vendido em cada mes e quais meses foram os melhores.")
    with col_b:
        st.markdown("#### Quais produtos vendem mais")
        st.write("Veja quais velas trazem mais lucro e mais faturamento para o negocio.")
    with col_c:
        st.markdown("#### Datas que aumentam as vendas")
        st.write("Veja como feriados e datas religiosas, como a Semana Santa, influenciam as vendas.")
else:
    tem_as_duas = analise_per is not None and analise_prod is not None

    # com as duas planilhas, mostra em abas separadas; com so uma, mostra direto
    if tem_as_duas:
        aba_per, aba_prod = st.tabs(["Vendas Mensais e Sazonalidade", "Produtos e Lucratividade"])
    else:
        aba_per = st.container()
        aba_prod = aba_per

    # --- SECAO 1: VENDAS MENSAIS ---
    if analise_per is not None:
        with aba_per:
            st.header("Analise de Vendas por Mes e Sazonalidade")
            st.write("Entenda como as vendas variam ao longo do ano e quais meses apresentam maior procura.")

            res_per = analise_per["resumo"]
            periodos = analise_per["periodos"]

            if "destaque" in analise_per:
                st.info(f"Resumo do Pico de Vendas: {analise_per['destaque']}")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Faturamento Total", reais(res_per["total_periodo"]), help="Soma total das vendas registradas nas planilhas")
            col2.metric("Media Mensal", reais(res_per["media"]), help="Valor medio vendido por mes")
            col3.metric("Mes de Maior Venda", res_per["pico"]["nome"], reais(res_per["pico"]["total"]), help="Mes com maior faturamento do ano")
            col4.metric("Mes de Menor Venda", res_per["fraco"]["nome"], reais(res_per["fraco"]["total"]), help="Mes com menor volume de vendas")

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Grafico de Faturamento por Mes")
            st.caption("As colunas mais altas indicam os meses em que a fabrica mais faturou:")

            df_p = pd.DataFrame(periodos).set_index("nome")
            st.bar_chart(df_p["total"], color="#f59e0b")

            st.subheader("Datas Comemorativas e Feriados Religiosos")
            st.write("Veja os feriados e datas religiosas presentes em cada mes que ajudam a explicar os aumentos nas vendas:")

            tabela_m = []
            for p in periodos:
                datas_str = ", ".join(p["datas"]) if p["datas"] else "Nenhum feriado principal neste mes"
                tabela_m.append({
                    "Mes": p["nome"],
                    "Faturamento Total": reais(p["total"]),
                    "Comparacao com Mes Anterior": f"{p['variacao_pct']}%" if p['variacao_pct'] is not None else "-",
                    "Datas Comemorativas e Feriados": datas_str
                })
            st.dataframe(pd.DataFrame(tabela_m), width="stretch", hide_index=True)

    # --- SECAO 2: ANALISE DE PRODUTOS ---
    if analise_prod is not None:
        with aba_prod:
            st.header("Analise de Desempenho dos Produtos")
            st.write("Descubra quais velas trazem mais receita e maior margem de lucro para a fabrica.")

            res_prod = analise_prod["resumo"]
            ranking = analise_prod["ranking"]

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Faturamento Total", reais(res_prod["faturamento_total"]), help="Valor total arrecadado com a venda dos produtos")
            col2.metric("Lucro Total", reais(res_prod["lucro_total"]), help="Lucro liquido obtido sobre os produtos")
            col3.metric("Margem Geral", f"{res_prod['margem_geral_pct']}%", help="Porcentagem media de lucro sobre o faturamento")
            col4.metric("Tipos de Produtos", res_prod["qtd_produtos"], help="Quantidade de itens diferentes analisados")

            st.subheader("Ranking de Produtos Mais Vendidos")
            st.caption("Os produtos no topo sao os que mais geraram faturamento:")
            top10 = {p["descricao"]: p["total"] for p in ranking[:10]}
            df_top = pd.DataFrame(top10.items(), columns=["descricao", "total"]).set_index("descricao")
            st.bar_chart(df_top["total"], color="#14b8a6")

            st.subheader("Vendas por Unidade (Kg vs Unidade)")
            st.caption("Divisao do faturamento entre vendas por quilo e vendas por unidade:")
            totais_unidade = {}
            for p in ranking:
                totais_unidade[p["unidade"]] = totais_unidade.get(p["unidade"], 0.0) + p["total"]
            df_un = pd.DataFrame(totais_unidade.items(), columns=["unidade", "total"]).set_index("unidade")
            st.bar_chart(df_un["total"], color="#8b5cf6")
            for unidade, total in totais_unidade.items():
                st.caption(f"{unidade}: {reais(total)}")

            st.subheader("Tabela de Desempenho Detalhado dos Produtos")
            st.write("Lista completa com quantidade vendida, receita, lucro obtido e margem de cada produto:")

            tabela_p = []
            for p in ranking:
                tabela_p.append({
                    "Descricao do Produto": p["descricao"],
                    "Quantidade Vendida": f"{p['quantidade']} {p['unidade']}",
                    "Faturamento Total": reais(p["total"]),
                    "Lucro Total": reais(p["lucro"]),
                    "Participacao (%)": f"{p['participacao_pct']}%",
                    "Margem de Lucro (%)": f"{p['margem_pct']}%",
                })
            st.dataframe(pd.DataFrame(tabela_p), width="stretch", hide_index=True)
