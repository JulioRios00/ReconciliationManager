from .base import Base
from .schema_public import *
from sqlalchemy import Column, Integer, TIMESTAMP, Boolean, String, text, DECIMAL, ForeignKey, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class Fligth(Base):

    __tablename__ = 'Fligth'
    __table_args__ = {'schema': 'ccs'}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DataCriacao = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    DataAtualizacao = Column(TIMESTAMP)
    Ativo = Column(Boolean, nullable=False, default=True)
    Excluido = Column(Boolean, nullable=False, default=False)
    IdUsuarioAlteracao = Column(UUID(as_uuid=True), ForeignKey('User.Id'))
    UsuarioAlteracao = relationship(User)
    Periodo = Column(Date, nullable=True)
  
    def __init__(self,periodo):
        self.Periodo = periodo

    def serialize(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}