# Análise de Vendas de Velas

Atividade extensionista do curso de Tecnologia em Banco de Dados, do Centro Universitário Internacional UNINTER.

**Proposta:** os donos da fábrica de velas Velas SC / Nova Aliança registram as vendas em um sistema de PDV, mas não conseguem usar esse mesmo sistema para analisar os dados do negócio, por causa da complexidade dele. O projeto usa a planilha que eles já conseguiam exportar do PDV para gerar uma análise simples de faturamento por mês, desempenho dos produtos e a relação entre os picos de venda e datas comemorativas e religiosas, como Páscoa e Dia das Mães.

**O que foi feito:** uma tela em Streamlit que lê a planilha, identifica sozinha se é de vendas mensais ou de produtos, salva os dados em um banco PostgreSQL (Supabase) e mostra os gráficos automaticamente.

**O que eu aprendi:** a lidar com planilhas reais, que vêm com nomes de coluna diferentes do esperado, e a pensar uma tela simples o bastante para quem nunca usou nenhum sistema antes.

Feito com Python, Streamlit, SQLAlchemy e PostgreSQL (Supabase).
