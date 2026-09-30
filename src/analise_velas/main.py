# Ponto de entrada do comando `analise-velas` ou `python -m analise_velas.main`
import os
import sys
from streamlit.web import cli as stcli


def rodar():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(diretorio_atual, "app.py")
    porta = os.getenv("PORT", "8501")
    
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.port",
        str(porta),
        "--server.address",
        "0.0.0.0",
        "--theme.base",
        "dark",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    rodar()
