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
    Date,
    Enum,
    func)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from src.enums.status_enum import StatusEnum

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
    # Fix: Explicitly specify foreign_keys parameter
    Configuracao = relationship("Configuration", foreign_keys=[ConfiguracaoId], overlaps="Flight")
    FlightDateId = Column(
        UUID(as_uuid=True),
        ForeignKey('ccs.FlightDate.Id'),
        nullable=True
    )
    FlightDate = relationship("FlightDate", foreign_keys=[FlightDateId], overlaps="Flight")
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

    TipoDeClasse = Column(String(10))
    Pacote = Column(String(50))
    DestinoPacket = Column(String(10))
    CodigoDoItem = Column(String(10))
    Descricao = Column(String(100))
    Provision1 = Column(String(10))
    Provision2 = Column(String(10))
    Tipo = Column(String(5))
    Svc = Column(Integer)
    # Foreign Key
    IdFlight = Column(UUID(as_uuid=True), ForeignKey('ccs.Flight.Id'))
    # Fix: Explicitly specify foreign_keys parameter
    Flight = relationship("Flight", foreign_keys=[IdFlight], overlaps="Configuracao")


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

    DataVoo = Column(Date)

    IdFlight = Column(UUID(as_uuid=True), ForeignKey('ccs.Flight.Id'))
    Flight = relationship("Flight", foreign_keys=[IdFlight], overlaps="FlightDate")

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

    Facility = Column(String(30))
    Organization = Column(String(30))
    PulledDate = Column(String(50))
    RunDate = Column(String(50))
    FacOrg = Column(String(30))
    SpcNr = Column(Integer)
    SpcDsc = Column(String(100))
    ActCatNm = Column(String(30))
    PrsStsCd = Column(String(100))
    PrcEffDt = Column(Date)
    PrcDisDt = Column(Date)
    PrcCurCd = Column(String(30))
    TotAmt = Column(DECIMAL(10, 2))
    LbrAmt = Column(DECIMAL(10, 2))
    PktNr = Column(Integer)
    PktNm = Column(String(100))
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


# CateringInvoiceReport
class CateringInvoiceReport(Base):
    __tablename__ = 'CateringInvoiceReport'
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

    Facility = Column(String)
    FltDate = Column(Date)
    FltNo = Column(String)
    FltInv = Column(String)
    Class = Column(String)
    ItemGroup = Column(String)
    Itemcode = Column(String)
    ItemDesc = Column(String)
    AlBillCode = Column(String)
    AlBillDesc = Column(String)
    BillCatg = Column(String)
    Unit = Column(String)
    Pax = Column(String)
    Qty = Column(String)
    UnitPrice = Column(String)
    TotalAmount = Column(String)

    def __init__(
        self, facility, flt_date, flt_no, flt_inv,
        class_, item_group, itemcode, item_desc,
        al_bill_code, al_bill_desc, bill_catg, unit,
        pax, qty, unit_price, total_amount
    ):
        self.Facility = facility
        self.FltDate = flt_date
        self.FltNo = flt_no
        self.FltInv = flt_inv
        self.Class = class_
        self.ItemGroup = item_group
        self.Itemcode = itemcode
        self.ItemDesc = item_desc
        self.AlBillCode = al_bill_code
        self.AlBillDesc = al_bill_desc
        self.BillCatg = bill_catg
        self.Unit = unit
        self.Pax = pax
        self.Qty = qty
        self.UnitPrice = unit_price
        self.TotalAmount = total_amount

    def serialize(self):
        return {
            c.name: str(getattr(self, c.name))
            for c in self.__table__.columns
        }


# mudar para AirCompanyInvoiceReport
class AirCompanyInvoiceReport(Base):
    __tablename__ = 'AirCompanyInvoiceReport'
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

    Supplier = Column(String)
    FlightDate = Column(Date)
    FlightNo = Column(String)
    Dep = Column(String)
    Arr = Column(String)
    Class = Column(String)
    InvoicedPax = Column(String)
    ServiceCode = Column(String)
    SupplierCode = Column(String)
    ServiceDescription = Column(String)
    Aircraft = Column(String)
    Qty = Column(Integer)
    UnitPrice = Column(DECIMAL(15, 2))
    SubTotal = Column(DECIMAL(15, 2))
    Tax = Column(DECIMAL(15, 2))
    TotalIncTax = Column(DECIMAL(15, 2))
    Currency = Column(String)
    ItemStatus = Column(String)
    InvoiceStatus = Column(String)
    InvoiceDate = Column(Date)
    PaidDate = Column(Date)
    FlightNoRed = Column(String)

    def __init__(
        self, supplier=None, flight_date=None, flight_no=None, dep=None,
        arr=None, class_=None, invoiced_pax=None, service_code=None,
        supplier_code=None, service_description=None, aircraft=None,
        qty=None, unit_price=None, sub_total=None, tax=None,
        total_inc_tax=None, currency=None, item_status=None,
        invoice_status=None, invoice_date=None, paid_date=None,
        flight_no_red=None
    ):
        self.Supplier = supplier
        self.FlightDate = flight_date
        self.FlightNo = flight_no
        self.Dep = dep
        self.Arr = arr
        self.Class = class_
        self.InvoicedPax = invoiced_pax
        self.ServiceCode = service_code
        self.SupplierCode = supplier_code
        self.ServiceDescription = service_description
        self.Aircraft = aircraft
        self.Qty = qty
        self.UnitPrice = unit_price
        self.SubTotal = sub_total
        self.Tax = tax
        self.TotalIncTax = total_inc_tax
        self.Currency = currency
        self.ItemStatus = item_status
        self.InvoiceStatus = invoice_status
        self.InvoiceDate = invoice_date
        self.PaidDate = paid_date
        self.FlightNoRed = flight_no_red

    def serialize(self):
        return {
            c.name: str(getattr(self, c.name))
            for c in self.__table__.columns
        }


class Reconciliation(Base):
    __tablename__ = 'Reconciliation'
    __table_args__ = {'schema': 'ccs', 'extend_existing': True}

    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DataCriacao = Column(DateTime, nullable=False, server_default=func.now())
    DataAtualizacao = Column(DateTime)
    Ativo = Column(Boolean, nullable=False, default=True)
    Excluido = Column(Boolean, nullable=False, default=False)
    
    # Air data
    AirSupplier = Column(String)
    AirFlightDate = Column(DateTime)
    AirFlightNo = Column(String)
    AirDep = Column(String)
    AirArr = Column(String)
    AirClass = Column(String)
    AirInvoicedPax = Column(String)
    AirServiceCode = Column(String)
    AirSupplierCode = Column(String)
    AirServiceDescription = Column(String)
    AirAircraft = Column(String)
    AirQty = Column(String)
    AirUnitPrice = Column(String)
    AirSubTotal = Column(String)
    AirTax = Column(String)
    AirTotalIncTax = Column(String)
    AirCurrency = Column(String)
    AirItemStatus = Column(String)
    AirInvoiceStatus = Column(String)
    AirInvoiceDate = Column(DateTime)
    AirPaidDate = Column(DateTime)
    AirFlightNoRed = Column(String)
    
    # Cat data
    CatFacility = Column(String)
    CatFltDate = Column(DateTime)
    CatFltNo = Column(String)
    CatFltInv = Column(String)
    CatClass = Column(String)
    CatItemGroup = Column(String)
    CatItemcode = Column(String)
    CatItemDesc = Column(String)
    CatAlBillCode = Column(String)
    CatAlBillDesc = Column(String)
    CatBillCatg = Column(String)
    CatUnit = Column(String)
    CatPax = Column(String)
    CatQty = Column(String)
    CatUnitPrice = Column(String)
    CatTotalAmount = Column(String)
    
    # Comparison flags
    Air = Column(String)
    Cat = Column(String)
    DifQty = Column(String)
    DifPrice = Column(String)
    AmountDif = Column(String)
    QtyDif = Column(String)
    
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'Id': str(self.Id),
            'DataCriacao': str(self.DataCriacao) if self.DataCriacao else None,
            'DataAtualizacao': str(self.DataAtualizacao) if self.DataAtualizacao else None,
            'Ativo': str(self.Ativo),
            'Excluido': str(self.Excluido),
            'AirSupplier': self.AirSupplier,
            'AirFlightDate': str(self.AirFlightDate) if self.AirFlightDate else None,
            'AirFlightNo': self.AirFlightNo,
            'AirDep': self.AirDep,
            'AirArr': self.AirArr,
            'AirClass': self.AirClass,
            'AirInvoicedPax': self.AirInvoicedPax,
            'AirServiceCode': self.AirServiceCode,
            'AirSupplierCode': self.AirSupplierCode,
            'AirServiceDescription': self.AirServiceDescription,
            'AirAircraft': self.AirAircraft,
            'AirQty': self.AirQty,
            'AirUnitPrice': self.AirUnitPrice,
            'AirSubTotal': self.AirSubTotal,
            'AirTax': self.AirTax,
            'AirTotalIncTax': self.AirTotalIncTax,
            'AirCurrency': self.AirCurrency,
            'AirItemStatus': self.AirItemStatus,
            'AirInvoiceStatus': self.AirInvoiceStatus,
            'AirInvoiceDate': str(self.AirInvoiceDate) if self.AirInvoiceDate else None,
            'AirPaidDate': str(self.AirPaidDate) if self.AirPaidDate else None,
            'AirFlightNoRed': self.AirFlightNoRed,
            'CatFacility': self.CatFacility,
            'CatFltDate': str(self.CatFltDate) if self.CatFltDate else None,
            'CatFltNo': self.CatFltNo,
            'CatFltInv': self.CatFltInv,
            'CatClass': self.CatClass,
            'CatItemGroup': self.CatItemGroup,
            'CatItemcode': self.CatItemcode,
            'CatItemDesc': self.CatItemDesc,
            'CatAlBillCode': self.CatAlBillCode,
            'CatAlBillDesc': self.CatAlBillDesc,
            'CatBillCatg': self.CatBillCatg,
            'CatUnit': self.CatUnit,
            'CatPax': self.CatPax,
            'CatQty': self.CatQty,
            'CatUnitPrice': self.CatUnitPrice,
            'CatTotalAmount': self.CatTotalAmount,
            'Air': self.Air,
            'Cat': self.Cat,
            'DifQty': self.DifQty,
            'DifPrice': self.DifPrice,
            'AmountDif': self.AmountDif,
            'QtyDif': self.QtyDif
        }


class FlightNumberMapping(Base):
    __tablename__ = 'FlightNumberMapping'
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

    AirCompanyFlightNumber = Column(String, nullable=True)
    CateringFlightNumber = Column(String, nullable=True)

    def __init__(self, air_company_flight_number=None,
                 catering_flight_number=None):
        self.AirCompanyFlightNumber = air_company_flight_number
        self.CateringFlightNumber = catering_flight_number

    def serialize(self):
        return {
            c.name: str(getattr(self, c.name))
            for c in self.__table__.columns
        }


class FlightClassMapping(Base):
    __tablename__ = 'FlightClassMapping'
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

    PromeusClass = Column(String, nullable=True)
    InflairClass = Column(String, nullable=True)

    ItemGroup = Column(String, nullable=True)
    ItemCode = Column(String, nullable=True)
    ItemDesc = Column(String, nullable=True)
    ALBillCode = Column(String, nullable=True)
    ALBillDesc = Column(String, nullable=True)
    BillCatg = Column(String, nullable=True)

    def __init__(self, promeus_class=None, inflair_class=None, item_group=None,
                 item_code=None, item_desc=None, al_bill_code=None,
                 al_bill_desc=None, bill_catg=None):
        self.PromeusClass = promeus_class  
        self.InflairClass = inflair_class
        self.ItemGroup = item_group
        self.ItemCode = item_code
        self.ItemDesc = item_desc
        self.ALBillCode = al_bill_code
        self.ALBillDesc = al_bill_desc
        self.BillCatg = bill_catg

    def serialize(self):
        return {
            c.name: str(getattr(self, c.name))
            for c in self.__table__.columns
        }


class ReconAnnotation(Base):
    __tablename__ = 'ReconAnnotation'
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

    ReconciliationId = Column(
        UUID(as_uuid=True),
        ForeignKey('ccs.Reconciliation.Id'),
        nullable=False
    )
    Reconciliation = relationship("Reconciliation", backref="annotations")

    Annotation = Column(String, nullable=False)
    Status = Column(Enum(StatusEnum), nullable=True, default=None)

    def __init__(self, reconciliation_id, annotation, status=None):
        self.ReconciliationId = reconciliation_id
        self.Annotation = annotation
        self.Status = status

    def serialize(self):
        return {
            c.name: str(getattr(self, c.name))
            for c in self.__table__.columns
        }