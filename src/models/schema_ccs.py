from .base import Base
from .schema_public import *
from sqlalchemy import (
    Column,
    Integer,
    TIMESTAMP,
    Boolean,
    String,
    text,
    DECIMAL,
    ForeignKey,
    Date)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime

import uuid


class Flight(Base):
    __tablename__ = 'Flight'
    __table_args__ = {'schema': 'ccs'}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DataCriacao = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )
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

    Meal = Column(Integer, nullable=True)
    Tray = Column(Integer, nullable=True)
    QtdPax = Column(Integer, nullable=True)
    ConfiguracaoId = (
        Column(
            UUID(as_uuid=True),
            ForeignKey('ccs.Configuration.Id'),
            nullable=True)
        )
    Configuracao = relationship("Configuration")
    FlightDateId = Column(
        UUID(as_uuid=True),
        ForeignKey('ccs.FlightDate.Id'),
        nullable=True
    )
    FlightDate = relationship("FlightDate")
    DataVoo = Column(Date, nullable=True)
    FlightReportId = (
        Column(
            UUID(as_uuid=True),
            ForeignKey('ccs.PriceReport.Id'),
            nullable=True
        )
    )
    FlightReport = relationship("PriceReport")

    def __init__(
        self, empresa_aerea, periodo, unidade, ciclo, vr_voo, origem, destino,
        hora_partida, hora_chegada, aeronave, meal=None, tray=None,
        qtd_pax=None, configuracao_id=None, flight_date_id=None,
        data_voo=None, flight_report_id=None
    ):
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
        self.Meal = meal
        self.Tray = tray
        self.QtdPax = qtd_pax
        self.ConfiguracaoId = configuracao_id
        self.FlightDateId = flight_date_id
        self.DataVoo = data_voo
        self.FlightReportId = flight_report_id

    def serialize(self):
        return {
            c.name: str(getattr(self, c.name))
            for c in self.__table__.columns
        }


class Configuration(Base):
    __tablename__ = 'Configuration'
    __table_args__ = {'schema': 'ccs'}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DataCriacao = (
        Column(TIMESTAMP,
               nullable=False,
               server_default=text("CURRENT_TIMESTAMP"))
        )
    DataAtualizacao = Column(TIMESTAMP)
    Ativo = Column(Boolean, nullable=False, default=True)
    Excluido = Column(Boolean, nullable=False, default=False)

    TipoDeClasse = Column(String(10), nullable=False)
    Pacote = Column(String(50), nullable=False)
    DestinoPacket = Column(String(10), nullable=False)
    CodigoDoItem = Column(String(10), nullable=False)
    Descricao = Column(String(100), nullable=False)
    Provision1 = Column(String(10), nullable=False)
    Provision2 = Column(String(10), nullable=False)
    Tipo = Column(String(5), nullable=False)
    Svc = Column(Integer, nullable=False)
    # Foreign Key
    IdFlight = Column(UUID(as_uuid=True), ForeignKey('ccs.Flight.Id'))
    # Lazy loading com nome correto
    Flight = relationship("Flight", lazy='joined')

    def __init__(
        self, tipo_de_classe, pacote, destino_packet, codigo_do_item,
        descricao, provision1, provision2, tipo, svc, id_flight
    ):
        self.TipoDeClasse = tipo_de_classe
        self.Pacote = pacote
        self.DestinoPacket = destino_packet
        self.CodigoDoItem = codigo_do_item
        self.Descricao = descricao
        self.Provision1 = provision1
        self.Provision2 = provision2
        self.Tipo = tipo
        self.Svc = svc
        self.IdFlight = id_flight

    def serialize(self):
        return {
            c.name: str(getattr(self, c.name))
            for c in self.__table__.columns
        }
 

class FlightDate(Base):
    __tablename__ = 'FlightDate'
    __table_args__ = {'schema': 'ccs'}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DataCriacao = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )
    DataAtualizacao = Column(TIMESTAMP)
    Ativo = Column(Boolean, nullable=False, default=True)
    Excluido = Column(Boolean, nullable=False, default=False)

    DataVoo = Column(Date, nullable=False)

    IdFlight = Column(UUID(as_uuid=True), ForeignKey('ccs.Flight.Id'))
    Flight = relationship("Flight", lazy='joined')

    def __init__(self, data_voo, id_flight):
        self.DataVoo = data_voo
        self.IdFlight = id_flight

    def serialize(self):
        return {
            c.name: str(getattr(self, c.name))
            for c in self.__table__.columns
            }


class PriceReport(Base):
    __tablename__ = 'PriceReport'
    __table_args__ = {'schema': 'ccs'}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DataCriacao = (
        Column(
            TIMESTAMP,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP")
            )
        )
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
    TotAmt = Column(DECIMAL(10, 2), nullable=False)
    LbrAmt = Column(DECIMAL(10, 2), nullable=False)
    PktNr = Column(Integer, nullable=False)
    PktNm = Column(String(100), nullable=False)
    SourceFile = Column(String(255), nullable=True)

    def __init__(self, facility, organization, pulled_date, run_date,
                 fac_org, spc_nr, spc_dsc, act_cat_nm, prs_sts_cd,
                 prc_eff_dt, prc_dis_dt, prc_cur_cd, tot_amt,
                 lbr_amt, pkt_nr, pkt_nm, source_file=None):
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
        self.LbrAmt = lbr_amt
        self.PktNr = pkt_nr
        self.PktNm = pkt_nm
        self.SourceFile = source_file

    def serialize(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class DataSource(Base):
    __tablename__ = 'DataSource'
    __table_args__ = {'schema': 'ccs'}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DataCriacao = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )
    DataAtualizacao = Column(TIMESTAMP)
    Ativo = Column(Boolean, nullable=False, default=True)
    Excluido = Column(Boolean, nullable=False, default=False)

    Source = Column(String(100), nullable=False)
    Page = Column(Integer, nullable=False)

    IdFlight = Column(
        UUID(as_uuid=True),
        ForeignKey('ccs.Flight.Id'),
        nullable=False
    )
    Flight = relationship(Flight, lazy='joined')

    def __init__(self, source, page, id_flight):
        self.Source = source
        self.Page = page
        self.IdFlight = id_flight

    def serialize(self):
        return {
            c.name: str(getattr(self, c.name))
            for c in self.__table__.columns
        }


class InvoiceHistory(Base):
    __tablename__ = 'InvoiceHistory'
    __table_args__ = {'schema': 'ccs'}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DataCriacao = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )
    DataAtualizacao = Column(TIMESTAMP)
    Ativo = Column(Boolean, nullable=False, default=True)
    Excluido = Column(Boolean, nullable=False, default=False)
    IdUsuarioAlteracao = Column(
        UUID(as_uuid=True),
        ForeignKey('User.Id'),
        nullable=True
    )
    UsuarioAlteracao = relationship(User)

    BrdFac = Column(String(20))
    BrdFltDt = Column(Date)
    BrdFltNr = Column(Integer)
    OpCd = Column(Integer)
    SrvDptStaCd = Column(String(10))
    SrvArrStaCd = Column(String(10))
    SrvFltNr = Column(Integer)
    SrvFltDt = Column(Date)
    Cos = Column(String(10))
    Psg = Column(Integer)
    Meal = Column(Integer)
    Tray = Column(Integer)
    Total = Column(DECIMAL(10, 2))
    Paid = Column(DECIMAL(10, 2))
    Variance = Column(DECIMAL(10, 2))
    GrandTotal = Column(DECIMAL(10, 2))
    OvdInd = Column(String(10))
    IvcPcsDt = Column(Date)
    IvcDbsDt = Column(Date)
    Org = Column(Integer)
    IvcSeqNr = Column(Integer)
    IvcCreDt = Column(Date)
    Comments = Column(String(255))
    LineSeqNr = Column(Integer)
    Item = Column(Integer)
    ActAmt = Column(DECIMAL(10, 2))
    ActQty = Column(Integer)
    SchAmt = Column(DECIMAL(10, 2))
    SchQty = Column(Integer)
    ActLbrAmt = Column(DECIMAL(10, 2))
    SchLbrAmt = Column(DECIMAL(10, 2))
    ItemDesc = Column(String(200))
    PktTyp = Column(String(40))
    PktNr = Column(Integer)
    PktNm = Column(String(50))
    PktVar = Column(Integer)
    SourceName = Column(String(255))
    Airline = Column(String(50))
    Currency = Column(String(10))
    ReconStatus = Column(String(20))
    BillingReference = Column(String(100))
    ImportedAt = Column(DateTime)

    def __init__(
        self, brd_fac, brd_flt_dt, brd_flt_nr, op_cd, srv_dpt_sta_cd,
        srv_arr_sta_cd, srv_flt_nr, srv_flt_dt, cos, psg, meal, tray, total,
        paid, variance, grand_total, ovd_ind, ivc_pcs_dt, ivc_dbs_dt,
        org, ivc_seq_nr, ivc_cre_dt, comments, line_seq_nr, item, act_amt,
        act_qty, sch_amt, sch_qty, act_lbr_amt, sch_lbr_amt, item_desc,
        pkt_typ=None, pkt_nr=None, pkt_nm=None, pkt_var=None, source_name=None,
        airline=None, currency=None, recon_status=None,
        billing_reference=None, imported_at=None
    ):
        self.BrdFac = brd_fac
        self.BrdFltDt = brd_flt_dt
        self.BrdFltNr = brd_flt_nr
        self.OpCd = op_cd
        self.SrvDptStaCd = srv_dpt_sta_cd
        self.SrvArrStaCd = srv_arr_sta_cd
        self.SrvFltNr = srv_flt_nr
        self.SrvFltDt = srv_flt_dt
        self.Cos = cos
        self.Psg = psg
        self.Meal = meal
        self.Tray = tray
        self.Total = total
        self.Paid = paid
        self.Variance = variance
        self.GrandTotal = grand_total
        self.OvdInd = ovd_ind
        self.IvcPcsDt = ivc_pcs_dt
        self.IvcDbsDt = ivc_dbs_dt
        self.Org = org
        self.IvcSeqNr = ivc_seq_nr
        self.IvcCreDt = ivc_cre_dt
        self.Comments = comments
        self.LineSeqNr = line_seq_nr
        self.Item = item
        self.ActAmt = act_amt
        self.ActQty = act_qty
        self.SchAmt = sch_amt
        self.SchQty = sch_qty
        self.ActLbrAmt = act_lbr_amt
        self.SchLbrAmt = sch_lbr_amt
        self.ItemDesc = item_desc
        self.PktTyp = pkt_typ
        self.PktNr = pkt_nr
        self.PktNm = pkt_nm
        self.PktVar = pkt_var
        self.SourceName = source_name
        self.Airline = airline
        self.Currency = currency
        self.ReconStatus = recon_status
        self.BillingReference = billing_reference
        self.ImportedAt = imported_at

    def serialize(self):
        return {
            c.name: str(getattr(self, c.name))
            for c in self.__table__.columns
        }
