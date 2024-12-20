from .base import Base
from .schema_public import *
from sqlalchemy import Column, Integer, TIMESTAMP, Boolean, String, text, DECIMAL, ForeignKey, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class Flight(Base):

    __tablename__ = 'Flight'
    __table_args__ = {'schema': 'ccs'}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DataCriacao = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    DataAtualizacao = Column(TIMESTAMP)
    Ativo = Column(Boolean, nullable=False, default=True)
    Excluido = Column(Boolean, nullable=False, default=False)
    IdUsuarioAlteracao = Column(UUID(as_uuid=True), ForeignKey('User.Id'))
    UsuarioAlteracao = relationship(User)
    EmpresaAerea = Column(String(50), nullable=False)
    Periodo = Column(String(30), nullable=True)
    Unidade = Column(String(10), nullable=False)
    Ciclo = Column(Integer, nullable=False)
    VrVoo = Column(Integer, nullable=False)
    Origem = Column(String(10), nullable=False)
    Destino = Column(String(10), nullable=False)
    HoraPartida = Column(String(10), nullable=False)
    HoraChegada = Column(String(10), nullable=False)
    Aeronave = Column(Integer, nullable=False)    
  
    def __init__(self, empresa_aerea, periodo, unidade, ciclo, vr_voo, origem, destino, hora_partida, hora_chegada, aeronave):
        self.EmpresaAerea = empresa_aerea
        self.Periodo = periodo
        self.Unidade = unidade
        self.Ciclo = ciclo
        self.VrVoo = vr_voo
        self.Origem = origem
        self.Destino = destino
        self.HoraPartida = hora_partida
        self.HoraChegada = hora_chegada
        self.Aeronave = aeronave

    def serialize(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class Configuration(Base):

    __tablename__ = 'Configuration'
    __table_args__ = {'schema': 'ccs'}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DataCriacao = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    DataAtualizacao = Column(TIMESTAMP)
    Ativo = Column(Boolean, nullable=False, default=True)
    Excluido = Column(Boolean, nullable=False, default=False)
    TipoDeClasse = Column(String(10), nullable=False)
    pacote = Column(String(50), nullable=False)
    destinoPacket = Column(String(10), nullable=False)
    CódigoDoItem = Column(String(10), nullable=False)
    Descrição = Column(String(100), nullable=False)
    Provision1 = Column(String(10), nullable=False)
    Provision2 = Column(String(10), nullable=False)
    Tipo = Column(String(5), nullable=False)
    Svc = Column(Integer, nullable=False)
    # Relationship to the 'Flight' table
    IdFligth = Column(UUID(as_uuid=True), ForeignKey('ccs.Flight.Id'))  # Foreign Key to Flight ID
    Fligth = relationship(Flight, lazy='joined')  # Link to Flight table

    def __init__(self, tipo_de_classe, pacote, destino_packet, código_doItem, descrição, provision1, provision2, tipo, svc, id_fligth):
        self.TipoDeClasse = tipo_de_classe
        self.pacote = pacote
        self.destinoPacket = destino_packet
        self.CódigoDoItem = código_doItem
        self.Descrição = descrição
        self.Provision1 = provision1
        self.Provision2 = provision2
        self.Tipo = tipo
        self.Svc = svc
        self.IdFligth = id_fligth


    def serialize(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
    

class FlightDate(Base):

    __tablename__ = 'FlightDate'
    __table_args__ = {'schema': 'ccs'}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DataCriacao = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    DataAtualizacao = Column(TIMESTAMP)
    Ativo = Column(Boolean, nullable=False, default=True)
    Excluido = Column(Boolean, nullable=False, default=False)
    Date = Column(Date)
    # Relationship to the 'Fligth' table
    IdFligth = Column(UUID(as_uuid=True), ForeignKey('ccs.Flight.Id'))  # Foreign Key to Fligth
    Flight = relationship(Flight, lazy='joined')  # Link to ht table

    def __init__(self, date, id_fligth):
        self.Date = date
        self.IdFligth = id_fligth

    def serialize(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
    

class PriceReport(Base):

    __tablename__ = 'PriceReport'
    __table_args__ = {'schema': 'ccs'}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DataCriacao = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    DataAtualizacao = Column(TIMESTAMP)
    Ativo = Column(Boolean, nullable=False, default=True)
    Excluido = Column(Boolean, nullable=False, default=False)
    Facility = Column(String(30), nullable=False)
    Organization = Column(String(30), nullable=False)
    PulledDate = Column(String(50), nullable=False)
    RunDate = Column(String(50), nullable=False)
    FacOrg = Column(String(30), nullable=False)
    SpcNr = Column(Integer, nullable=False)
    SpcDsc = Column(String(100), nullable=False)
    ActCatNm = Column(String(30), nullable=False)
    PrsStsCd = Column(String(100), nullable=False)
    PrcEffDt = Column(Date, nullable=False)
    PrcDisDt = Column(Date, nullable=False)
    PrcCurCd = Column(String(30), nullable=False)
    TotAmt = Column(DECIMAL, nullable=False)
    LbrAmt = Column(DECIMAL, nullable=False)
    PktNr = Column(Integer, nullable=False)
    PktNm = Column(String(100), nullable=False)

    def __init__(self, facility, organization, pulled_date, run_date, fac_org, spc_nr, spc_dsc, act_cat_nm, prs_sts_cd, prc_eff_dt, prc_dis_dt, prc_cur_cd, tot_amt, abr_amt, pkt_nr, pkt_nm):
        self.Facility = facility
        self.Organization = organization
        self.PulledDate = pulled_date
        self.RunDate = run_date
        self.FacOrg = fac_org
        self.SpcNr = spc_nr
        self.SpcDsc = spc_dsc
        self.ActCatNm = act_cat_nm
        self.PrsStsCd = prs_sts_cd
        self.PrcEffDt = prc_eff_dt
        self.PrcDisDt = prc_dis_dt
        self.PrcCurCd = prc_cur_cd
        self.TotAmt = tot_amt
        self.LbrAmt = abr_amt
        self.PktNr = pkt_nr
        self.PktNm = pkt_nm

    def serialize(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class DataSourc(Base):

    __tablename__ = 'DataSource'
    __table_args__ = {'schema': 'ccs'}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DataCriacao = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    DataAtualizacao = Column(TIMESTAMP)
    Ativo = Column(Boolean, nullable=False, default=True)
    Excluido = Column(Boolean, nullable=False, default=False)
    Source = Column(String(100), nullable=False)
    Page = Column(Integer, nullable=False)
    # Relationship to the 'Flight' table
    IdFligth = Column(UUID(as_uuid=True), ForeignKey('ccs.Flight.Id'))  # Foreign Key to Flight
    Flight = relationship(Flight, lazy='joined')  # Link to Flight table

    def __init__(self, source, page, id_fligth):
        self.Source = source
        self.Page = page
        self.IdFligth = id_fligth

    def serialize(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
    