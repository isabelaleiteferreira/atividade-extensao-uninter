import sys
import os

# Adiciona o diretório src ao path do Python para importação dos módulos do pacote
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from analise_velas.app import *
