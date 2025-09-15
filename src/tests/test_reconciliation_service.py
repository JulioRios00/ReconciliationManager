from datetime import date, datetime
from unittest.mock import MagicMock, Mock

import pytest
from sqlalchemy.orm import Session

from models.schema_ccs import (
    AirCompanyInvoiceReport,
    CateringInvoiceReport,
    Reconciliation,
)
from repositories.reconciliation_repository import ReconciliationRepository

# Import your application modules
from services.reconciliation_service import ReconciliationService


@pytest.fixture
def mock_db_session():
    """Mock database session for testing"""
    return Mock(spec=Session)


@pytest.fixture
def mock_reconciliation_repository(mock_db_session):
    """Mock reconciliation repository"""
    repo = Mock(spec=ReconciliationRepository)
    return repo


@pytest.fixture
def reconciliation_service(mock_db_session, mock_reconciliation_repository):
    """Create reconciliation service with mocked dependencies"""
    service = ReconciliationService(mock_db_session)
    service.reconciliation_repository = mock_reconciliation_repository
    return service


class TestReconciliationService:
    """Test cases for ReconciliationService"""

    def test_parse_date_valid_date_string(self, reconciliation_service):
        """Test _parse_date with valid date string"""
        result = reconciliation_service._parse_date("2023-01-15")
        expected = date(2023, 1, 15)
        assert result == expected

    def test_parse_date_valid_datetime_string(self, reconciliation_service):
        """Test _parse_date with valid datetime string"""
        result = reconciliation_service._parse_date("2023-01-15 10:30:00")
        expected = date(2023, 1, 15)
        assert result == expected

    def test_parse_date_invalid_string(self, reconciliation_service):
        """Test _parse_date with invalid date string"""
        result = reconciliation_service._parse_date("invalid-date")
        assert result is None

    def test_parse_date_none_input(self, reconciliation_service):
        """Test _parse_date with None input"""
        result = reconciliation_service._parse_date(None)
        assert result is None

    def test_get_all_reconciliation_data_success(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test successful retrieval of all reconciliation data"""
        # Mock data
        mock_record = Mock()
        mock_record.serialize.return_value = {"id": 1, "name": "test"}
        mock_reconciliation_repository.get_all.return_value = [mock_record]

        result = reconciliation_service.get_all_reconciliation_data()

        assert "data" in result
        assert len(result["data"]) == 1
        mock_reconciliation_repository.get_all.assert_called_once()

    def test_get_all_reconciliation_data_exception(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test exception handling in get_all_reconciliation_data"""
        mock_reconciliation_repository.get_all.side_effect = Exception("Database error")

        result = reconciliation_service.get_all_reconciliation_data()

        # Result is a tuple: (response_dict, status_code)
        response_dict, status_code = result
        assert "message" in response_dict
        assert "error" in response_dict
        assert status_code == 501

    def test_get_paginated_data_with_all_parameters(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test paginated data with all parameters (date range, flight number, item name)"""
        mock_record = Mock()
        mock_record.serialize.return_value = {"id": 1}
        mock_reconciliation_repository.get_by_date_range.return_value = [mock_record]
        mock_reconciliation_repository.get_count_by_date_range.return_value = 1

        result = reconciliation_service.get_paginated_reconciliation_data(
            limit=10,
            offset=0,
            filter_type="all",
            start_date="2023-01-01",
            end_date="2023-01-31",
            flight_number="FL123",
            item_name="test_item",
        )

        assert "data" in result
        assert "pagination" in result
        assert "filters" in result
        mock_reconciliation_repository.get_by_date_range.assert_called_once()

    def test_get_paginated_data_with_date_and_item_name(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test paginated data with date range and item name"""
        mock_record = Mock()
        mock_record.serialize.return_value = {"id": 1}
        mock_reconciliation_repository.get_by_item_name_and_date_range.return_value = [
            mock_record
        ]
        mock_reconciliation_repository.get_count_by_item_name_and_date_range.return_value = (
            1
        )

        result = reconciliation_service.get_paginated_reconciliation_data(
            limit=10,
            offset=0,
            filter_type="all",
            start_date="2023-01-01",
            end_date="2023-01-31",
            item_name="test_item",
        )

        assert "data" in result
        assert result["filters"]["item_name"] == "test_item"
        mock_reconciliation_repository.get_by_item_name_and_date_range.assert_called_once()

    def test_get_paginated_data_with_flight_and_item_name(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test paginated data with flight number and item name"""
        mock_record = Mock()
        mock_record.serialize.return_value = {"id": 1}
        mock_reconciliation_repository.get_by_item_name_and_flight_number.return_value = [
            mock_record
        ]
        mock_reconciliation_repository.get_count_by_item_name_and_flight_number.return_value = (
            1
        )

        result = reconciliation_service.get_paginated_reconciliation_data(
            limit=10,
            offset=0,
            filter_type="all",
            flight_number="FL123",
            item_name="test_item",
        )

        assert "data" in result
        assert result["filters"]["flight_number"] == "FL123"
        mock_reconciliation_repository.get_by_item_name_and_flight_number.assert_called_once()

    def test_get_paginated_data_with_date_range_only(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test paginated data with date range only"""
        mock_record = Mock()
        mock_record.serialize.return_value = {"id": 1}
        mock_reconciliation_repository.get_by_date_range.return_value = [mock_record]
        mock_reconciliation_repository.get_count_by_date_range.return_value = 1

        result = reconciliation_service.get_paginated_reconciliation_data(
            limit=10,
            offset=0,
            filter_type="all",
            start_date="2023-01-01",
            end_date="2023-01-31",
        )

        assert "data" in result
        assert result["filters"]["start_date"] == "2023-01-01"
        mock_reconciliation_repository.get_by_date_range.assert_called_once()

    def test_get_paginated_data_with_flight_number_only(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test paginated data with flight number only"""
        mock_record = Mock()
        mock_record.serialize.return_value = {"id": 1}
        mock_reconciliation_repository.get_by_flight_number.return_value = [mock_record]
        mock_reconciliation_repository.get_count_by_flight_number.return_value = 1

        result = reconciliation_service.get_paginated_reconciliation_data(
            limit=10, offset=0, filter_type="all", flight_number="FL123"
        )

        assert "data" in result
        assert result["filters"]["flight_number"] == "FL123"
        mock_reconciliation_repository.get_by_flight_number.assert_called_once()

    def test_get_paginated_data_with_item_name_only(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test paginated data with item name only"""
        mock_record = Mock()
        mock_record.serialize.return_value = {"id": 1}
        mock_reconciliation_repository.get_by_item_name.return_value = [mock_record]
        mock_reconciliation_repository.get_count_by_item_name.return_value = 1

        result = reconciliation_service.get_paginated_reconciliation_data(
            limit=10, offset=0, filter_type="all", item_name="test_item"
        )

        assert "data" in result
        assert result["filters"]["item_name"] == "test_item"
        mock_reconciliation_repository.get_by_item_name.assert_called_once()

    def test_get_paginated_data_no_filters(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test paginated data with no filters"""
        mock_record = Mock()
        mock_record.serialize.return_value = {"id": 1}
        mock_reconciliation_repository.get_paginated.return_value = [mock_record]
        mock_reconciliation_repository.get_count.return_value = 1

        result = reconciliation_service.get_paginated_reconciliation_data(
            limit=10, offset=0, filter_type="all"
        )

        assert "data" in result
        assert result["pagination"]["total"] == 1
        mock_reconciliation_repository.get_paginated.assert_called_once()

    def test_get_paginated_data_with_filtered_type(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test paginated data with filtered type"""
        mock_record = Mock()
        mock_record.serialize.return_value = {"id": 1}
        mock_reconciliation_repository.get_filtered_paginated.return_value = [
            mock_record
        ]
        mock_reconciliation_repository.get_filtered_count.return_value = 1

        result = reconciliation_service.get_paginated_reconciliation_data(
            limit=10, offset=0, filter_type="matched"
        )

        assert "data" in result
        assert result["filters"]["filter_type"] == "matched"
        mock_reconciliation_repository.get_filtered_paginated.assert_called_once()

    def test_get_paginated_data_exception(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test exception handling in get_paginated_reconciliation_data"""
        mock_reconciliation_repository.get_paginated.side_effect = Exception(
            "Database error"
        )

        result = reconciliation_service.get_paginated_reconciliation_data()

        # Result is a tuple: (response_dict, status_code)
        response_dict, status_code = result
        assert "message" in response_dict
        assert "error" in response_dict
        assert status_code == 501

    def test_get_reconciliation_summary_success(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test successful reconciliation summary generation"""
        # Create mock records with required attributes
        mock_record1 = Mock()
        mock_record1.Air = "Yes"
        mock_record1.Cat = "Yes"
        mock_record1.DifQty = "No"
        mock_record1.DifPrice = "No"
        mock_record1.AmountDif = "10.50"

        mock_record2 = Mock()
        mock_record2.Air = "Yes"
        mock_record2.Cat = "No"
        mock_record2.DifQty = "Yes"
        mock_record2.DifPrice = "No"
        mock_record2.AmountDif = "5.25"

        mock_record3 = Mock()
        mock_record3.Air = "No"
        mock_record3.Cat = "Yes"
        mock_record3.DifQty = "No"
        mock_record3.DifPrice = "Yes"
        mock_record3.AmountDif = "0.00"

        mock_reconciliation_repository.get_all.return_value = [
            mock_record1,
            mock_record2,
            mock_record3,
        ]

        result = reconciliation_service.get_reconciliation_summary()

        assert "summary" in result
        summary = result["summary"]
        assert summary["total_records"] == 3
        assert summary["matching_records"] == 1
        assert summary["air_only_records"] == 1
        assert summary["cat_only_records"] == 1
        assert summary["quantity_discrepancies"] == 1
        assert summary["price_discrepancies"] == 1
        assert summary["total_discrepancies"] == 2
        assert summary["total_amount_difference"] == 15.75

    def test_get_reconciliation_summary_exception(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test exception handling in get_reconciliation_summary"""
        mock_reconciliation_repository.get_all.side_effect = Exception("Database error")

        result = reconciliation_service.get_reconciliation_summary()

        # Result is a tuple: (response_dict, status_code)
        response_dict, status_code = result
        assert "message" in response_dict
        assert "error" in response_dict
        assert status_code == 501

    def test_get_invoice_reports_data_air_only(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test invoice reports data with air reports only"""
        mock_record = Mock()
        mock_record.serialize.return_value = {"id": 1}
        mock_reconciliation_repository.get_air_company_invoice_reports.return_value = [
            mock_record
        ]
        mock_reconciliation_repository.get_air_company_invoice_reports_count.return_value = (
            1
        )

        result = reconciliation_service.get_invoice_reports_data(report_type="air")

        assert "air_company_reports" in result
        assert "pagination" in result
        assert "filters" in result
        assert result["filters"]["report_type"] == "air"
        assert result["air_company_reports"]["total_count"] == 1

    def test_get_invoice_reports_data_catering_only(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test invoice reports data with catering reports only"""
        mock_record = Mock()
        mock_record.serialize.return_value = {"id": 1}
        mock_reconciliation_repository.get_catering_invoice_reports.return_value = [
            mock_record
        ]
        mock_reconciliation_repository.get_catering_invoice_reports_count.return_value = (
            1
        )

        result = reconciliation_service.get_invoice_reports_data(report_type="catering")

        assert "catering_reports" in result
        assert "pagination" in result
        assert "filters" in result
        assert result["filters"]["report_type"] == "catering"
        assert result["catering_reports"]["total_count"] == 1

    def test_get_invoice_reports_data_both(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test invoice reports data with both report types"""
        mock_air_record = Mock()
        mock_air_record.serialize.return_value = {"id": 1, "type": "air"}
        mock_cat_record = Mock()
        mock_cat_record.serialize.return_value = {"id": 2, "type": "catering"}

        mock_reconciliation_repository.get_air_company_invoice_reports.return_value = [
            mock_air_record
        ]
        mock_reconciliation_repository.get_air_company_invoice_reports_count.return_value = (
            1
        )
        mock_reconciliation_repository.get_catering_invoice_reports.return_value = [
            mock_cat_record
        ]
        mock_reconciliation_repository.get_catering_invoice_reports_count.return_value = (
            1
        )

        result = reconciliation_service.get_invoice_reports_data(report_type="both")

        assert "air_company_reports" in result
        assert "catering_reports" in result
        assert "pagination" in result
        assert result["filters"]["report_type"] == "both"
        assert result["air_company_reports"]["total_count"] == 1
        assert result["catering_reports"]["total_count"] == 1

    def test_get_invoice_reports_data_with_filters(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test invoice reports data with date and flight filters"""
        mock_record = Mock()
        mock_record.serialize.return_value = {"id": 1}
        mock_reconciliation_repository.get_air_company_invoice_reports.return_value = [
            mock_record
        ]
        mock_reconciliation_repository.get_air_company_invoice_reports_count.return_value = (
            1
        )

        result = reconciliation_service.get_invoice_reports_data(
            report_type="air",
            start_date="2023-01-01",
            end_date="2023-01-31",
            flight_number="FL123",
        )

        assert "air_company_reports" in result
        assert result["filters"]["start_date"] == "2023-01-01"
        assert result["filters"]["end_date"] == "2023-01-31"
        assert result["filters"]["flight_number"] == "FL123"

    def test_get_invoice_reports_data_exception(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test exception handling in get_invoice_reports_data"""
        mock_reconciliation_repository.get_air_company_invoice_reports.side_effect = (
            Exception("Database error")
        )

        result = reconciliation_service.get_invoice_reports_data()

        # Result is a tuple: (response_dict, status_code)
        response_dict, status_code = result
        assert "message" in response_dict
        assert "error" in response_dict
        assert status_code == 501

    def test_safe_int_valid_value(self, reconciliation_service):
        """Test _safe_int with valid integer string"""
        result = reconciliation_service._safe_int("42")
        assert result == 42

    def test_safe_int_invalid_value(self, reconciliation_service):
        """Test _safe_int with invalid value"""
        result = reconciliation_service._safe_int("invalid")
        assert result == 0

    def test_safe_int_none_value(self, reconciliation_service):
        """Test _safe_int with None value"""
        result = reconciliation_service._safe_int(None)
        assert result == 0

    def test_safe_float_valid_value(self, reconciliation_service):
        """Test _safe_float with valid float string"""
        result = reconciliation_service._safe_float("42.5")
        assert result == 42.5

    def test_safe_float_comma_separator(self, reconciliation_service):
        """Test _safe_float with comma as decimal separator"""
        result = reconciliation_service._safe_float("42,5")
        assert result == 42.5

    def test_safe_float_invalid_value(self, reconciliation_service):
        """Test _safe_float with invalid value"""
        result = reconciliation_service._safe_float("invalid")
        assert result == 0.0

    def test_populate_reconciliation_table_success(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test successful population of reconciliation table"""
        # Mock air and catering records
        air_record = Mock()
        air_record.FlightDate = date(2023, 1, 15)
        air_record.FlightNo = "AA123"
        air_record.AirSupplier = "American Airlines"
        air_record.Qty = 100

        cat_record = Mock()
        cat_record.FltDate = date(2023, 1, 15)
        cat_record.FltNo = "AA123"
        cat_record.Facility = "JFK"
        cat_record.Qty = 95

        # Mock the session and query methods
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.delete.return_value = 0
        mock_query.all.return_value = [air_record, cat_record]
        reconciliation_service.session = mock_session

        result = reconciliation_service.populate_reconciliation_table()

        assert result["success"] is True
        assert "message" in result

    def test_populate_reconciliation_table_exception(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test population with database exception"""
        # Mock the session to raise an exception
        mock_session = Mock()
        mock_session.query.side_effect = Exception("DB Error")
        reconciliation_service.session = mock_session

        result = reconciliation_service.populate_reconciliation_table()

        assert result["success"] is False
        assert "error" in result["message"].lower()

    def test_calculate_reconciliation_differences(self, reconciliation_service):
        """Test calculation of reconciliation differences"""
        # Mock matched records
        mock_record = Mock()
        mock_record.AirQty = "100"
        mock_record.CatQty = "95"
        mock_record.AirSubTotal = "1000.00"
        mock_record.CatTotalAmount = "950.00"

        # Mock the session and query
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_record]
        reconciliation_service.session = mock_session

        reconciliation_service._calculate_reconciliation_differences()

        # Verify the record was updated
        assert mock_record.DifQty == "Yes"
        assert mock_record.QtyDif == "-5"  # cat_qty - air_qty
        assert mock_record.DifPrice == "Yes"
        assert mock_record.AmountDif == "-50.0"  # cat_total - air_subtotal

    def test_get_reconciliation_summary_with_data(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test reconciliation summary with actual data"""
        mock_record1 = Mock()
        mock_record1.Difference = 10
        mock_record1.Air = "Yes"
        mock_record1.Cat = "Yes"

        mock_record2 = Mock()
        mock_record2.Difference = -5
        mock_record2.Air = "Yes"
        mock_record2.Cat = "No"

        mock_reconciliation_repository.get_all.return_value = [
            mock_record1,
            mock_record2,
        ]

        result = reconciliation_service.get_reconciliation_summary()

        assert result["summary"]["total_records"] == 2
        assert result["summary"]["matching_records"] == 1
        assert result["summary"]["air_only_records"] == 1
        assert result["summary"]["cat_only_records"] == 0

    def test_get_reconciliation_summary_empty(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test reconciliation summary with no data"""
        mock_reconciliation_repository.get_all.return_value = []

        result = reconciliation_service.get_reconciliation_summary()

        assert result["summary"]["total_records"] == 0
        assert result["summary"]["matching_records"] == 0
        assert result["summary"]["air_only_records"] == 0
        assert result["summary"]["cat_only_records"] == 0

    def test_get_reconciliation_summary_with_exception_handling(
        self, reconciliation_service, mock_reconciliation_repository
    ):
        """Test reconciliation summary with exception"""
        mock_reconciliation_repository.get_all.side_effect = Exception("DB Error")

        result = reconciliation_service.get_reconciliation_summary()

        # Result is a tuple: (response_dict, status_code)
        response_dict, status_code = result
        assert "message" in response_dict
        assert "error" in response_dict
        assert status_code == 501
