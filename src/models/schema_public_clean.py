from sqlalchemy import Table
from sqlalchemy.orm import relationship

from .base import Base

try:
    from ..common.conexao_banco import engine
except ImportError:
    from common.conexao_banco import engine


cliente = Table("Cliente", Base.metadata, autoload_with=engine)


class Cliente(Base):
    __table__ = cliente


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
