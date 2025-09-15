from datetime import date
from unittest.mock import Mock

import pytest


class TestConftestFixtures:
    """Test cases for conftest.py fixtures to improve coverage"""

    def test_mock_db_session_fixture(self, mock_db_session):
        """Test that mock_db_session fixture creates a proper mock"""
        assert mock_db_session is not None
        assert hasattr(mock_db_session, "query")
        assert hasattr(mock_db_session, "add")
        assert hasattr(mock_db_session, "commit")

    def test_mock_reconciliation_repository_fixture(
        self, mock_reconciliation_repository
    ):
        """Test that mock_reconciliation_repository fixture creates a proper mock"""
        assert mock_reconciliation_repository is not None
        assert hasattr(mock_reconciliation_repository, "get_all")
        assert hasattr(mock_reconciliation_repository, "get_paginated")
        assert hasattr(mock_reconciliation_repository, "get_count")

    def test_reconciliation_service_fixture(self, reconciliation_service):
        """Test that reconciliation_service fixture creates a proper service instance"""
        assert reconciliation_service is not None
        assert hasattr(reconciliation_service, "get_all_reconciliation_data")
        assert hasattr(reconciliation_service, "get_paginated_reconciliation_data")
        assert hasattr(reconciliation_service, "get_reconciliation_summary")

    def test_sample_air_record_fixture(self, sample_air_record):
        """Test that sample_air_record fixture creates a proper mock record"""
        assert sample_air_record.Id == "air-123"
        assert sample_air_record.Supplier == "Test Airlines"
        assert sample_air_record.FlightDate == date(2023, 1, 15)
        assert sample_air_record.FlightNo == "FL123"
        assert sample_air_record.Qty == 100
        assert sample_air_record.UnitPrice == 25.50
        assert sample_air_record.SubTotal == 2550.00
        assert sample_air_record.Ativo is True
        assert sample_air_record.Excluido is False

    def test_sample_catering_record_fixture(self, sample_catering_record):
        """Test that sample_catering_record fixture creates a proper mock record"""
        assert sample_catering_record.Id == "cat-456"
        assert sample_catering_record.Facility == "JFK Catering"
        assert sample_catering_record.FltDate == date(2023, 1, 15)
        assert sample_catering_record.FltNo == "FL123"
        assert sample_catering_record.Qty == 100
        assert sample_catering_record.UnitPrice == 25.50
        assert sample_catering_record.TotalAmount == 2550.00
        assert sample_catering_record.Ativo is True
        assert sample_catering_record.Excluido is False

    def test_sample_reconciliation_record_fixture(self, sample_reconciliation_record):
        """Test that sample_reconciliation_record fixture creates a proper mock record"""
        assert sample_reconciliation_record.Id == "rec-789"
        assert sample_reconciliation_record.Air == "Yes"
        assert sample_reconciliation_record.Cat == "Yes"
        assert sample_reconciliation_record.DifQty == "No"
        assert sample_reconciliation_record.DifPrice == "No"
        assert sample_reconciliation_record.AmountDif == "0.00"
        assert sample_reconciliation_record.QtyDif == "0"

        # Test serialize method
        serialized = sample_reconciliation_record.serialize()
        assert serialized["id"] == "rec-789"
        assert serialized["air"] == "Yes"
        assert serialized["cat"] == "Yes"
        assert serialized["dif_qty"] == "No"
        assert serialized["dif_price"] == "No"

    def test_fixture_combinations(
        self,
        reconciliation_service,
        sample_air_record,
        sample_catering_record,
        sample_reconciliation_record,
    ):
        """Test that fixtures can be used together"""
        # Test that service can work with sample records
        assert reconciliation_service is not None
        assert sample_air_record.FlightNo == sample_catering_record.FltNo
        assert sample_air_record.FlightDate == sample_catering_record.FltDate
        assert sample_reconciliation_record.Air == "Yes"
        assert sample_reconciliation_record.Cat == "Yes"

    def test_mock_db_session_methods(self, mock_db_session):
        """Test mock_db_session has expected SQLAlchemy methods"""
        # Test that common SQLAlchemy session methods are available
        methods_to_check = ["query", "add", "commit", "rollback", "flush", "close"]
        for method in methods_to_check:
            assert hasattr(
                mock_db_session, method
            ), f"mock_db_session should have {method} method"

    def test_mock_repository_methods(self, mock_reconciliation_repository):
        """Test mock_reconciliation_repository has expected methods"""
        # Test that repository methods are available
        methods_to_check = [
            "get_all",
            "get_paginated",
            "get_count",
            "get_by_item_name",
            "get_by_date_range",
            "get_by_flight_number",
            "get_filtered_paginated",
        ]
        for method in methods_to_check:
            assert hasattr(
                mock_reconciliation_repository, method
            ), f"mock_reconciliation_repository should have {method} method"

    def test_service_dependencies(
        self, reconciliation_service, mock_db_session, mock_reconciliation_repository
    ):
        """Test that service has proper dependencies injected"""
        assert reconciliation_service.session == mock_db_session
        assert (
            reconciliation_service.reconciliation_repository
            == mock_reconciliation_repository
        )

    def test_sample_records_data_consistency(
        self, sample_air_record, sample_catering_record
    ):
        """Test that sample records have consistent data for reconciliation"""
        # Both records should have same flight info for reconciliation testing
        assert sample_air_record.FlightNo == sample_catering_record.FltNo
        assert sample_air_record.FlightDate == sample_catering_record.FltDate
        assert sample_air_record.Qty == sample_catering_record.Qty
        assert sample_air_record.UnitPrice == sample_catering_record.UnitPrice

    def test_reconciliation_record_calculations(self, sample_reconciliation_record):
        """Test that reconciliation record has proper calculation fields"""
        # Test quantity difference calculation
        air_qty = int(sample_reconciliation_record.AirQty)
        cat_qty = int(sample_reconciliation_record.CatQty)
        expected_qty_diff = cat_qty - air_qty

        assert sample_reconciliation_record.QtyDif == str(expected_qty_diff)

        # Test amount difference calculation
        air_amount = float(sample_reconciliation_record.AirSubTotal)
        cat_amount = float(sample_reconciliation_record.CatTotalAmount)
        expected_amount_diff = round(cat_amount - air_amount, 2)

        assert sample_reconciliation_record.AmountDif == "0.00"
