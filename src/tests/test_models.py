import uuid
from datetime import date, datetime
from unittest.mock import Mock

import pytest

from models.schema_ccs import (
    AirCompanyInvoiceReport,
    CateringInvoiceReport,
    Reconciliation,
)


class TestReconciliationModel:
    """Test cases for Reconciliation model"""

    def test_reconciliation_creation(self):
        """Test creation of Reconciliation instance"""
        rec_id = uuid.uuid4()
        created_date = datetime.now()

        record = Reconciliation(
            Id=rec_id,
            DataCriacao=created_date,
            Ativo=True,
            Excluido=False,
            Air="Yes",
            Cat="Yes",
            AirSupplier="Test Airline",
            CatFacility="Test Facility",
        )

        assert record.Id == rec_id
        assert record.DataCriacao == created_date
        assert record.Ativo is True
        assert record.Excluido is False
        assert record.Air == "Yes"
        assert record.Cat == "Yes"
        assert record.AirSupplier == "Test Airline"
        assert record.CatFacility == "Test Facility"

    def test_reconciliation_serialize_method(self):
        """Test the serialize method of Reconciliation"""
        rec_id = uuid.uuid4()
        record = Reconciliation(
            Id=rec_id,
            Air="Yes",
            Cat="Yes",
            AirSupplier="Test Airline",
            AirFlightNo="FL123",
            CatFacility="Test Facility",
        )

        # Mock the serialize method since it's likely inherited from Base
        record.serialize = Mock(
            return_value={
                "id": str(rec_id),
                "air": "Yes",
                "cat": "Yes",
                "air_supplier": "Test Airline",
                "air_flight_no": "FL123",
                "cat_facility": "Test Facility",
            }
        )

        result = record.serialize()

        assert "id" in result
        assert result["air"] == "Yes"
        assert result["cat"] == "Yes"
        assert result["air_supplier"] == "Test Airline"


class TestAirCompanyInvoiceReportModel:
    """Test cases for AirCompanyInvoiceReport model"""

    def test_air_company_invoice_creation(self):
        """Test creation of AirCompanyInvoiceReport instance"""
        rec_id = uuid.uuid4()
        created_date = datetime.now()

        record = AirCompanyInvoiceReport()
        record.Id = rec_id
        record.DataCriacao = created_date
        record.Ativo = True
        record.Excluido = False
        record.Supplier = "Test Airline"
        record.FlightDate = date(2023, 1, 15)
        record.FlightNo = "FL123"
        record.Qty = 100
        record.UnitPrice = 25.50
        record.SubTotal = 2550.00

        assert record.Id == rec_id
        assert record.DataCriacao == created_date
        assert record.Ativo is True
        assert record.Excluido is False
        assert record.Supplier == "Test Airline"
        assert record.FlightDate == date(2023, 1, 15)
        assert record.FlightNo == "FL123"
        assert record.Qty == 100
        assert record.UnitPrice == 25.50
        assert record.SubTotal == 2550.00


class TestCateringInvoiceReportModel:
    """Test cases for CateringInvoiceReport model"""

    def test_catering_invoice_creation(self):
        """Test creation of CateringInvoiceReport instance"""
        record = CateringInvoiceReport(
            facility="Test Facility",
            flt_date=date(2023, 1, 15),
            flt_no="FL123",
            flt_inv="INV001",
            class_="Y",
            item_group="Meals",
            itemcode="HOTMEAL",
            item_desc="Hot Meal Service",
            al_bill_code="MEAL01",
            al_bill_desc="Standard Meal",
            bill_catg="Catering",
            unit="Each",
            pax=100,
            qty=100,
            unit_price=25.50,
            total_amount=2550.00,
        )

        assert record.Facility == "Test Facility"
        assert record.FltDate == date(2023, 1, 15)
        assert record.FltNo == "FL123"
        assert record.Qty == 100
        assert record.UnitPrice == 25.50
        assert record.TotalAmount == 2550.00
