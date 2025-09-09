import uuid
from email.policy import default

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base

try:
    from ..common.conexao_banco import engine
except:
    from common.conexao_banco import engine


categoria_empresa = Table("CategoriaEmpresa", Base.metadata, autoload_with=engine)


class CategoriaEmpresa(Base):

    __table__ = categoria_empresa

    def serialize(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class CategoriaArquivo(Base):

    __tablename__ = "CategoriaArquivo"
    __table_args__ = {"schema": "public", "extend_existing": True}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DataCriacao = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    DataAtualizacao = Column(TIMESTAMP)
    Ativo = Column(Boolean, nullable=False, default=True)
    Excluido = Column(Boolean, nullable=False, default=False)
    IdCategoria = Column(
        UUID(as_uuid=True), ForeignKey("CategoriaEmpresa.Id"), index=True
    )
    Categoria = relationship(CategoriaEmpresa)
    TipoArquivo = Column(Text)
    Qtd = Column(Integer)
    Obs = Column(Text)
    Extensao = Column(String(50))

    def __init__(self, IdCategoria, TipoArquivo, Qtd, Obs, Extensao):
        self.IdCategoria = IdCategoria
        self.TipoArquivo = TipoArquivo
        self.Qtd = Qtd
        self.Obs = Obs
        self.Extensao = Extensao

    def serialize(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


cfop = Table("Cfop", Base.metadata, autoload_with=engine)


class Cfop(Base):

    __table__ = cfop


empresa_cnae = Table("EmpresaCnae", Base.metadata, autoload_with=engine)


class EmpresaCnae(Base):

    __table__ = empresa_cnae


cliente = Table("Cliente", Base.metadata, autoload_with=engine)


class Cliente(Base):
    __table__ = cliente


empresa = Table("Empresa", Base.metadata, autoload_with=engine)


class Empresa(Base):

    __table__ = empresa


group = Table("Group", Base.metadata, autoload_with=engine)


class Group(Base):
    __table__ = group


userGroup = Table("UserGroup", Base.metadata, autoload_with=engine)


class UserGroup(Base):
    __table__ = userGroup


user = Table("User", Base.metadata, autoload_with=engine)


class User(Base):
    __table__ = user
    Cliente = relationship(Cliente)
    groups = relationship(Group, secondary=userGroup, viewonly=True)


arquivo_upload = Table("ArquivoUpload", Base.metadata, autoload_with=engine)


class ArquivoUpload(Base):

    __table__ = arquivo_upload

    def serialize(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class ArquivoUploadEmpresa(Base):

    __tablename__ = "ArquivoUploadEmpresa"
    __table_args__ = {"schema": "public", "extend_existing": True}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    IdEmpresa = Column(UUID(as_uuid=True), ForeignKey("Empresa.Id"), index=True)
    Empresa = relationship(Empresa)
    DataCriacao = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    DataAtualizacao = Column(TIMESTAMP)
    Ativo = Column(Boolean, nullable=False, default=True)
    Excluido = Column(Boolean, nullable=False, default=False)
    IdUsuarioAlteracao = Column(UUID(as_uuid=True), ForeignKey("User.Id"))
    UsuarioAlteracao = relationship(User)
    TipoArquivo = Column(Text)
    Qtd = Column(Integer)
    Obs = Column(Text, default="")
    DataInicio = Column(Date)
    DataFim = Column(Date)
    Extensao = Column(String(50))

    def __init__(
        self, IdEmpresa, TipoArquivo, Qtd, Extensao, DataInicio=None, DataFim=None
    ):
        self.IdEmpresa = IdEmpresa
        self.TipoArquivo = TipoArquivo
        self.Qtd = Qtd
        self.Extensao = Extensao
        self.DataInicio = DataInicio
        self.DataFim = DataFim

    def serialize(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class StoredFiles(Base):

    __tablename__ = "StoredFiles"
    __table_args__ = {"schema": "public", "extend_existing": True}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    IdEmpresa = Column(UUID(as_uuid=True), ForeignKey("Empresa.Id"), index=True)
    Empresa = relationship(Empresa)
    DataCriacao = Column(TIMESTAMP, nullable=False, default=text("CURRENT_TIMESTAMP"))
    DataAtualizacao = Column(TIMESTAMP)
    Ativo = Column(Boolean, nullable=False, default=True)
    Excluido = Column(Boolean, nullable=False, default=False)
    IdUsuarioAlteracao = Column(UUID(as_uuid=True), ForeignKey("User.Id"))
    UsuarioAlteracao = relationship(User)
    TipoDoArquivo = Column(String(50))
    NomeDoArquivo = Column(Text, nullable=False)
    key = Column(Text)
    ArquivoOk = Column(Boolean)

    def init(self, IdEmpresa, TipoDoArquivo, NomeDoArquivo, key, ArquivoOk):
        self.IdEmpresa = IdEmpresa
        self.TipoDoArquivo = TipoDoArquivo
        self.NomeDoArquivo = NomeDoArquivo
        self.key = key
        self.ArquivoOk = ArquivoOk

    def serialize(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


tipi = Table("Tipi", Base.metadata, autoload_with=engine)


class Tipi(Base):

    __table__ = tipi

    def serialize(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
