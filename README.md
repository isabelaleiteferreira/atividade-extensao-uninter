# 🕯️ Análise de Vendas de Velas (Streamlit + Supabase PostgreSQL)

Plataforma em **Streamlit** que lê planilhas de vendas exportadas do PDV de uma fábrica de velas, gera análises financeiras e relatórios de produtos, e relaciona os meses de maior venda com datas comemorativas e religiosas (ex: Páscoa / Semana Santa). Projeto de TCC — CST em Banco de Dados.

Desenvolvido em **Python** com **Streamlit**, **SQLAlchemy** e **PostgreSQL (Supabase)**.

---

## 📁 Estrutura do Projeto

```text
├── app.py                      # Ponto de entrada do Streamlit
├── requirements.txt            # Dependências para instalação via pip / Render
├── pyproject.toml              # Gerenciamento de pacotes via `uv`
├── .env                        # Variáveis de ambiente (conexão com Supabase)
├── .env.example                # Exemplo de configuração do .env
├── src/analise_velas/
│   ├── app.py                  # Código da interface gráfica Streamlit
│   ├── database.py             # Tabelas e conexão com o Supabase (SQLAlchemy)
│   ├── main.py                 # Script de execução para o Render
│   └── services/
│       ├── analise.py          # Lógica de cálculo de faturamento e lucro
│       ├── calendario.py       # Cálculo da Páscoa e datas religiosas
│       └── leitura.py          # Leitura e parsing de arquivos Excel
└── exemplos_dados/             # Planilhas reais de teste (Plan1.xlsx e Plan2.xlsx)
```

---

## 🚀 Como Rodar Localmente

1. **Instalar dependências**:
   ```bash
   uv sync
   ```
   *(ou `pip install -r requirements.txt`)*

2. **Verificar tabelas no Supabase**:
   ```bash
   uv run python -m analise_velas.database
   ```

3. **Iniciar a aplicação**:
   ```bash
   uv run streamlit run app.py
   ```
   *(ou `uv run python -m analise_velas.main`)*

4. Acesse no seu navegador: **`http://localhost:8501`**.

---

## ☁️ Passo a Passo para Publicar no Render (Web Service Gratuito)

Quando você tiver acesso à sua conta do GitHub, siga estas etapas para publicar a aplicação gratuitamente no **Render**:

### Passo 1: Subir o projeto para o GitHub
1. Crie um novo repositório no seu GitHub (pode ser Público ou Privado).
2. Faça o upload ou `git push` dos arquivos deste projeto.

### Passo 2: Criar o Web Service no Render
1. Acesse o [Render Dashboard](https://dashboard.render.com/) e faça login.
2. Clique no botão **New +** no canto superior e selecione **Web Service**.
3. Conecte sua conta do GitHub e selecione o repositório do projeto.

### Passo 3: Configurar os Parâmetros de Build
No formulário de criação do Web Service, preencha:
- **Name**: `analise-velas` (ou o nome de sua preferência)
- **Region**: Oregon (US West) ou Frankfurt (EU)
- **Branch**: `main`
- **Root Directory**: *(deixe em branco)*
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  pip install uv && uv sync
  ```
  *(ou `pip install -r requirements.txt`)*
- **Start Command**:
  ```bash
  uv run python -m analise_velas.main
  ```
  *(ou `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`)*
- **Instance Type**: `Free`

### Passo 4: Adicionar a Variável de Ambiente do Banco
1. No final da mesma página, clique em **Advanced** -> **Add Environment Variable**.
2. Adicione a variável:
   - **Key**: `DATABASE_URL`
   - **Value**: a mesma string de conexão que está no seu arquivo `.env` local
3. Clique em **Create Web Service**.

### Passo 5: Acessar a aplicação
O Render irá compilar o projeto e disponibilizar um link público (ex: `https://analise-velas.onrender.com`) para você e os avaliadores do TCC acessarem em qualquer celular ou computador!
