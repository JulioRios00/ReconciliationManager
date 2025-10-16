import os
import sys
from datetime import date, datetime
from unittest.mock import MagicMock, Mock

import pytest
from sqlalchemy.orm import Session

from src.repositories.reconciliation_repository import ReconciliationRepository

# Import your application modules
from src.services.reconciliation_service import ReconciliationService

# Add src directory to Python path for imports
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))
if src_path not in sys.path:
    sys.path.insert(0, src_path)


@pytest.fixture
def mock_db_session():
    """Mock database session for testing"""
    session = Mock(spec=Session)
    return session


@pytest.fixture
def mock_reconciliation_repository(mock_db_session):
    """Mock reconciliation repository"""
    repo = Mock(spec=ReconciliationRepository)
    repo.session = mock_db_session
    return repo


@pytest.fixture
def reconciliation_service(mock_db_session, mock_reconciliation_repository):
    """Create reconciliation service with mocked dependencies"""
    service = ReconciliationService(mock_db_session)
    service.reconciliation_repository = mock_reconciliation_repository
    return service


@pytest.fixture
def sample_air_record():
    """Sample air company invoice record for testing"""
    record = Mock()
    record.Id = "air-123"
    record.Supplier = "Test Airlines"
    record.FlightDate = date(2023, 1, 15)
    record.FlightNo = "FL123"
    record.Dep = "JFK"
    record.Arr = "LAX"
    record.Class = "Y"
    record.InvoicedPax = 100
    record.ServiceCode = "MEAL"
    record.SupplierCode = "TA001"
    record.ServiceDescription = "In-flight meal service"
    record.Aircraft = "B737"
    record.Qty = 100
    record.UnitPrice = 25.50
    record.SubTotal = 2550.00
    record.Tax = 255.00
    record.TotalIncTax = 2805.00
    record.Currency = "USD"
    record.ItemStatus = "Active"
    record.InvoiceStatus = "Paid"
    record.InvoiceDate = date(2023, 1, 16)
    record.PaidDate = date(2023, 1, 20)
    record.FlightNoRed = "FL123R"
    record.Ativo = True
    record.Excluido = False
    return record


@pytest.fixture
def sample_catering_record():
    """Sample catering invoice record for testing"""
    record = Mock()
    record.Id = "cat-456"
    record.Facility = "JFK Catering"
    record.FltDate = date(2023, 1, 15)
    record.FltNo = "FL123"
    record.FltInv = "INV001"
    record.Class = "Y"
    record.ItemGroup = "Meals"
    record.Itemcode = "HOTMEAL"
    record.ItemDesc = "Hot Meal Service"
    record.AlBillCode = "MEAL01"
    record.AlBillDesc = "Standard Meal"
    record.BillCatg = "Catering"
    record.Unit = "Each"
    record.Pax = 100
    record.Qty = 100
    record.UnitPrice = 25.50
    record.TotalAmount = 2550.00
    record.Ativo = True
    record.Excluido = False
    return record


@pytest.fixture
def sample_reconciliation_record():
    """Sample reconciliation record for testing"""
    record = Mock()
    record.Id = "rec-789"
    record.Air = "Yes"
    record.Cat = "Yes"
    record.DifQty = "No"
    record.DifPrice = "No"
    record.AmountDif = "0.00"
    record.QtyDif = "0"
    record.AirQty = "100"
    record.CatQty = "100"
    record.AirSubTotal = "2550.00"
    record.CatTotalAmount = "2550.00"
    record.serialize.return_value = {
        "id": "rec-789",
        "air": "Yes",
        "cat": "Yes",
        "dif_qty": "No",
        "dif_price": "No",
    }
    return record
