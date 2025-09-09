from .base import Base
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
try:
    from src.enums.status_enum import StatusEnum
except ImportError:
    from enums.status_enum import StatusEnum

import uuid


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
    FlightDate = Column(Date, nullable=True)
    FlightNo = Column(String)
    Dep = Column(String)
    Arr = Column(String)
    Class = Column(String)
    InvoicedPax = Column(String)
    ServiceCode = Column(String)
    SupplierCode = Column(String, nullable=True)
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
    InvoiceDate = Column(Date, nullable=True)
    PaidDate = Column(Date, nullable=True)
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
    
    Annotations = relationship(
        "ReconAnnotation",
        back_populates="Reconciliation",
        cascade="all, delete-orphan",
        order_by="ReconAnnotation.DataCriacao"
    )

    
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
            'QtyDif': self.QtyDif,
            'Annotations': [a.serialize() for a in self.Annotations] if self.Annotations else []
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
    Reconciliation = relationship(
        "Reconciliation",
        back_populates="Annotations"
    )

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
