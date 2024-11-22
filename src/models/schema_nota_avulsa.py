from .base import Base
from sqlalchemy import Table
from sqlalchemy import Column, String, ForeignKey, Integer, TIMESTAMP, Boolean, Date, text, Text, Float, DECIMAL, NUMERIC
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
try:
    from ..common.conexao_banco import engine
except:
    from common.conexao_banco import engine


dados_ipi = Table('dados_ipi', Base.metadata, autoload_with=engine, schema='nota_avulsa')

class DadosIpi(Base):

    __table__ = dados_ipi


# nota_entrada = Table('nota', Base.metadata, autoload_with=engine, schema='nota_avulsa')

# class NotaEntrada(Base):

#     __table__ = nota_entrada


dados_icms = Table('dados_icms', Base.metadata, autoload_with=engine, schema='nota_avulsa')

class DadosIcms(Base):

    __table__ = dados_icms


dados_itens = Table('dados_itens', Base.metadata, autoload_with=engine, schema='nota_avulsa')

class DadosItens(Base):

    __table__ = dados_itens


empresa_nota_avulsa = Table('empresa', Base.metadata, autoload_with=engine, schema='nota_avulsa')

class EmpresaNotaAvulsa(Base):

    __table__ = empresa_nota_avulsa
    
    def serialize(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


dados_nota = Table('dados_nota', Base.metadata, autoload_with=engine, schema='nota_avulsa')

class DadosNota(Base):

    __table__ = dados_nota


dados_pessoa = Table('dados_pessoa', Base.metadata, autoload_with=engine, schema='nota_avulsa')

class DadosPessoa(Base):

    __table__ = dados_pessoa


totais = Table('totais', Base.metadata, autoload_with=engine, schema='nota_avulsa')

class Totais(Base):

    __table__ = totais


dados_transporte = Table('dados_transporte', Base.metadata, autoload_with=engine, schema='nota_avulsa')

class DadosTransporte(Base):

    __table__ = dados_transporte
        
        
dados_suframa = Table('dados_suframa', Base.metadata, autoload_with=engine, schema='nota_avulsa')

class DadosSuframa(Base):

    __table__ = dados_suframa

    def serialize(self):
            return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class NotaEntrada(Base):
    __tablename__ = 'nota'
    __table_args__ = {'schema': 'nota_avulsa'}

    id_nota_entrada = Column(Integer, primary_key=True)
    chave = Column(String(44))
    cnpj_emitente = Column(String(14))
    data_emissao = Column(TIMESTAMP)
    key_s3 = Column(String(255))
    razao_emitente = Column(String(60))
    tipo_manifestacao = Column(String(30))
    valor = Column(NUMERIC(19,2))
    empresa_id = Column(Integer, ForeignKey('nota_avulsa.empresa.id'))
    id_dados_nota = Column(Integer, ForeignKey('nota_avulsa.dados_nota.id_dados_nota'))
    data_nota = Column(Date)
    status = Column(String(255))
    cnpj_empresa = Column(String(14))
    analise_ml = Column(String())
    status_nota = Column(String(255))
    tipo_nota = Column(String(255))
    DATA_INCLUSAO = Column(TIMESTAMP)
    erro_pedido = Column(String(50))
    erro_recebimento = Column(String(1))
   
    def __init__(self, id_nota_entrada, chave, cnpj_emitente, data_emissao, key_s3, razao_emitente, tipo_manifestacao,
                 valor,empresa_id,id_dados_nota,data_nota,status,cnpj_empresa, analise_ml, status_nota, tipo_nota, DATA_INCLUSAO,
                 erro_pedido, erro_recebimento):
        self.id_nota_entrada = id_nota_entrada
        self.chave = chave
        self.cnpj_emitente = cnpj_emitente
        self.data_emissao = data_emissao
        self.key_s3 = key_s3
        self.razao_emitente = razao_emitente
        self.tipo_manifestacao = tipo_manifestacao
        self.valor = valor
        self.empresa_id = empresa_id
        self.id_dados_nota = id_dados_nota
        self.data_nota = data_nota
        self.status = status
        self.cnpj_empresa = cnpj_empresa
        self.analise_ml = analise_ml
        self.status_nota = status_nota
        self.tipo_nota = tipo_nota
        self.DATA_INCLUSAO = DATA_INCLUSAO
        self.erro_pedido = erro_pedido
        self.erro_recebimento = erro_recebimento
