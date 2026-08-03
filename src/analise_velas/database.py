# conexao e tabelas do banco de dados (PostgreSQL no Supabase)
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# a URL do banco fica no arquivo .env (nao e commitada no git)
URL = os.getenv("DATABASE_URL")

# connect_timeout evita travar se o banco demorar para responder
# pool_timeout evita travar se todas as conexoes estiverem em uso
engine = create_engine(
    URL,
    pool_pre_ping=True,
    pool_timeout=15,
    connect_args={"connect_timeout": 10},
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Importacao(Base):
    # guarda cada envio de planilha
    __tablename__ = "importacoes"
    id = Column(Integer, primary_key=True)
    nome_arquivo = Column(String(255))
    tipo_planilha = Column(String(20))
    data_importacao = Column(DateTime, default=datetime.utcnow)
    total_registros = Column(Integer)


class VendaMensal(Base):
    # vendas de cada mes
    __tablename__ = "vendas_mensais"
    id = Column(Integer, primary_key=True)
    importacao_id = Column(Integer, ForeignKey("importacoes.id"))
    data_inicial = Column(Date)
    mes = Column(Integer)
    ano = Column(Integer)
    total = Column(Float)


class Produto(Base):
    # os produtos (velas)
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True)
    codigo = Column(Integer)
    descricao = Column(String(255), unique=True)


class VendaProduto(Base):
    # vendas de cada produto
    __tablename__ = "vendas_produto"
    id = Column(Integer, primary_key=True)
    importacao_id = Column(Integer, ForeignKey("importacoes.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Float)
    total = Column(Float)
    lucro = Column(Float)


def criar_tabelas():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    criar_tabelas()
    print("tabelas criadas com sucesso no Supabase!")
