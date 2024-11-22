from .base import Base
from sqlalchemy import Table
try:
    from ..common.conexao_banco import engine
except:
    from common.conexao_banco import engine
    

aliquota_icms = Table('AliquotaIcms', Base.metadata, autoload_with=engine, schema='maketheprice')

class AliquotaIcms(Base):

    __table__ = aliquota_icms



erro_aliquota_icms = Table('ErroAliquotaIcms', Base.metadata, autoload_with=engine, schema='maketheprice')

class ErroAliquotaIcms(Base):

    __table__ = erro_aliquota_icms

    def serialize(self):
        return {c.name: str(getattr(self, c.name))
            for c in self.__table__.columns}



estoque_produto = Table('EstoqueProduto', Base.metadata, autoload_with=engine, schema='maketheprice')

class EstoqueProduto(Base):

    __table__ = estoque_produto

    def serialize(self):
        return {c.name: str(getattr(self, c.name))
            for c in self.__table__.columns}



itemnota = Table('ItemNota', Base.metadata, autoload_with=engine, schema='maketheprice')

class ItemNota(Base):

    __table__ = itemnota



ncm_lessin = Table('NcmLessin', Base.metadata, autoload_with=engine, schema='maketheprice')

class NcmLessin(Base):

    __table__ = ncm_lessin



nota = Table('Nota', Base.metadata, autoload_with=engine, schema='maketheprice')

class Nota(Base):

    __table__ = nota



produto_ficha3 = Table('ProdutoFicha3', Base.metadata, autoload_with=engine, schema='maketheprice')

class ProdutoFicha3(Base):

    __table__ = produto_ficha3

    def serialize(self):
        return {c.name: str(getattr(self, c.name))
            for c in self.__table__.columns}



ficha3 = Table('Ficha3', Base.metadata, autoload_with=engine, schema='maketheprice')

class Ficha3(Base):

    __table__ = ficha3

    def serialize(self):
        return {c.name: str(getattr(self, c.name))
            for c in self.__table__.columns}