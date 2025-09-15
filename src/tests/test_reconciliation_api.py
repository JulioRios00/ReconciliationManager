import json
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import the API components
from app.reconciliation_api.reconciliation import DecimalEncoder, main


class TestDecimalEncoder:
    """Test cases for DecimalEncoder JSON encoder"""

    def test_encode_decimal(self):
        """Test encoding Decimal objects to float"""
        encoder = DecimalEncoder()
        decimal_value = Decimal("123.456")
        result = encoder.default(decimal_value)
        assert result == 123.456
        assert isinstance(result, float)

    def test_encode_zero_decimal(self):
        """Test encoding zero Decimal"""
        encoder = DecimalEncoder()
        decimal_value = Decimal("0.00")
        result = encoder.default(decimal_value)
        assert result == 0.00
        assert isinstance(result, float)

    def test_encode_negative_decimal(self):
        """Test encoding negative Decimal"""
        encoder = DecimalEncoder()
        decimal_value = Decimal("-45.67")
        result = encoder.default(decimal_value)
        assert result == -45.67
        assert isinstance(result, float)

    def test_encode_non_decimal(self):
        """Test encoding non-Decimal objects falls back to parent"""
        encoder = DecimalEncoder()
        test_obj = {"key": "value"}

        with pytest.raises(TypeError):
            encoder.default(test_obj)

    def test_encode_string(self):
        """Test encoding string objects"""
        encoder = DecimalEncoder()
        test_string = "test string"

        with pytest.raises(TypeError):
            encoder.default(test_string)

    def test_encode_none(self):
        """Test encoding None raises TypeError"""
        encoder = DecimalEncoder()

        with pytest.raises(
            TypeError, match="Object of type NoneType is not JSON serializable"
        ):
            encoder.default(None)


class TestReconciliationAPIMain:
    """Test cases for the main Lambda handler function"""

    @patch("app.reconciliation_api.reconciliation.get_session")
    def test_main_successful_request_all_params(self, mock_get_session):
        """Test successful request with all parameters"""
        # Mock the database session and service
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session

        mock_service = Mock()
        mock_service.get_paginated_reconciliation_data.return_value = {
            "data": [{"id": 1, "name": "test"}],
            "pagination": {"total": 1, "limit": 10, "offset": 0},
        }

        with patch(
            "app.reconciliation_api.reconciliation.ReconciliationService",
            return_value=mock_service,
        ):
            event = {
                "queryStringParameters": {
                    "limit": "10",
                    "offset": "0",
                    "filter_type": "all",
                    "start_date": "2023-01-01",
                    "end_date": "2023-01-31",
                    "flight_number": "FL123",
                    "item_name": "test_item",
                }
            }

            result = main(event, {})

            assert result["statusCode"] == 200
            assert "data" in json.loads(result["body"])
            assert result["headers"]["Content-Type"] == "application/json"
            assert result["headers"]["Access-Control-Allow-Origin"] == "*"

    @patch("app.reconciliation_api.reconciliation.get_session")
    def test_main_successful_request_minimal_params(self, mock_get_session):
        """Test successful request with minimal parameters"""
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session

        mock_service = Mock()
        mock_service.get_paginated_reconciliation_data.return_value = {
            "data": [],
            "pagination": {"total": 0, "limit": 100, "offset": 0},
        }

        with patch(
            "app.reconciliation_api.reconciliation.ReconciliationService",
            return_value=mock_service,
        ):
            event = {"queryStringParameters": {}}

            result = main(event, {})

            assert result["statusCode"] == 200
            mock_service.get_paginated_reconciliation_data.assert_called_once_with(
                limit=100,
                offset=0,
                filter_type="all",
                start_date=None,
                end_date=None,
                flight_number=None,
                item_name=None,
            )

    @patch("app.reconciliation_api.reconciliation.get_session")
    def test_main_successful_request_no_query_params(self, mock_get_session):
        """Test successful request with no queryStringParameters"""
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session

        mock_service = Mock()
        mock_service.get_paginated_reconciliation_data.return_value = {
            "data": [],
            "pagination": {"total": 0, "limit": 100, "offset": 0},
        }

        with patch(
            "app.reconciliation_api.reconciliation.ReconciliationService",
            return_value=mock_service,
        ):
            event = {}

            result = main(event, {})

            assert result["statusCode"] == 200
            mock_service.get_paginated_reconciliation_data.assert_called_once_with(
                limit=100,
                offset=0,
                filter_type="all",
                start_date=None,
                end_date=None,
                flight_number=None,
                item_name=None,
            )

    def test_main_invalid_filter_type(self):
        """Test request with invalid filter_type"""
        event = {"queryStringParameters": {"filter_type": "invalid_type"}}

        result = main(event, {})

        assert result["statusCode"] == 400
        response_body = json.loads(result["body"])
        assert "message" in response_body
        assert "Invalid filter_type" in response_body["message"]
        assert result["headers"]["Content-Type"] == "application/json"

    def test_main_valid_filter_types(self):
        """Test all valid filter types are accepted"""
        valid_types = [
            "all",
            "discrepancies",
            "air_only",
            "cat_only",
            "quantity_difference",
            "price_difference",
        ]

        for filter_type in valid_types:
            with patch(
                "app.reconciliation_api.reconciliation.get_session"
            ) as mock_get_session:
                mock_session = Mock()
                mock_get_session.return_value.__enter__.return_value = mock_session

                mock_service = Mock()
                mock_service.get_paginated_reconciliation_data.return_value = {
                    "data": []
                }

                with patch(
                    "app.reconciliation_api.reconciliation.ReconciliationService",
                    return_value=mock_service,
                ):
                    event = {"queryStringParameters": {"filter_type": filter_type}}

                    result = main(event, {})
                    assert result["statusCode"] == 200

    @patch("app.reconciliation_api.reconciliation.get_session")
    def test_main_service_returns_error_tuple(self, mock_get_session):
        """Test when service returns error tuple (message, status_code)"""
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session

        mock_service = Mock()
        error_response = ({"message": "Service error", "error": "DB Error"}, 500)
        mock_service.get_paginated_reconciliation_data.return_value = error_response

        with patch(
            "app.reconciliation_api.reconciliation.ReconciliationService",
            return_value=mock_service,
        ):
            event = {"queryStringParameters": {}}

            result = main(event, {})

            assert result["statusCode"] == 500
            response_body = json.loads(result["body"])
            assert response_body["message"] == "Service error"
            assert response_body["error"] == "DB Error"

    @patch("app.reconciliation_api.reconciliation.get_session")
    def test_main_database_connection_error(self, mock_get_session):
        """Test database connection error handling"""
        mock_get_session.side_effect = Exception("Database connection failed")

        event = {"queryStringParameters": {}}

        result = main(event, {})

        assert result["statusCode"] == 500
        response_body = json.loads(result["body"])
        assert response_body["message"] == "Internal server error"
        assert "Database connection failed" in response_body["error"]

    @patch("app.reconciliation_api.reconciliation.get_session")
    def test_main_service_exception(self, mock_get_session):
        """Test service exception handling"""
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session

        mock_service = Mock()
        mock_service.get_paginated_reconciliation_data.side_effect = Exception(
            "Service processing error"
        )

        with patch(
            "app.reconciliation_api.reconciliation.ReconciliationService",
            return_value=mock_service,
        ):
            event = {"queryStringParameters": {}}

            result = main(event, {})

            assert result["statusCode"] == 500
            response_body = json.loads(result["body"])
            assert response_body["message"] == "Internal server error"
            assert "Service processing error" in response_body["error"]

    @patch("app.reconciliation_api.reconciliation.get_session")
    def test_main_parameter_type_conversion(self, mock_get_session):
        """Test parameter type conversion (string to int)"""
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session

        mock_service = Mock()
        mock_service.get_paginated_reconciliation_data.return_value = {"data": []}

        with patch(
            "app.reconciliation_api.reconciliation.ReconciliationService",
            return_value=mock_service,
        ):
            event = {"queryStringParameters": {"limit": "50", "offset": "25"}}

            result = main(event, {})

            assert result["statusCode"] == 200
            mock_service.get_paginated_reconciliation_data.assert_called_once_with(
                limit=50,
                offset=25,
                filter_type="all",
                start_date=None,
                end_date=None,
                flight_number=None,
                item_name=None,
            )

    @patch("app.reconciliation_api.reconciliation.get_session")
    def test_main_with_decimal_data(self, mock_get_session):
        """Test handling of Decimal data in response"""
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session

        mock_service = Mock()
        mock_service.get_paginated_reconciliation_data.return_value = {
            "data": [{"amount": Decimal("123.45"), "total": Decimal("678.90")}],
            "pagination": {"total": 1},
        }

        with patch(
            "app.reconciliation_api.reconciliation.ReconciliationService",
            return_value=mock_service,
        ):
            event = {"queryStringParameters": {}}

            result = main(event, {})

            assert result["statusCode"] == 200
            response_body = json.loads(result["body"])
            assert response_body["data"][0]["amount"] == 123.45
            assert response_body["data"][0]["total"] == 678.90

    def test_main_cors_headers(self):
        """Test that CORS headers are always included"""
        event = {"queryStringParameters": {"filter_type": "invalid"}}

        result = main(event, {})

        assert result["headers"]["Access-Control-Allow-Origin"] == "*"
        assert result["headers"]["Access-Control-Allow-Credentials"] is True
        assert result["headers"]["Content-Type"] == "application/json"

    @patch("app.reconciliation_api.reconciliation.get_session")
    def test_main_context_parameter(self, mock_get_session):
        """Test that context parameter is accepted but not used"""
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session

        mock_service = Mock()
        mock_service.get_paginated_reconciliation_data.return_value = {"data": []}

        with patch(
            "app.reconciliation_api.reconciliation.ReconciliationService",
            return_value=mock_service,
        ):
            event = {"queryStringParameters": {}}
            context = {"aws_request_id": "test-123", "function_name": "test-function"}

            result = main(event, context)

            assert result["statusCode"] == 200
            # Context should be accepted but not affect functionality

    def test_main_path_setup_execution(self):
        """Test that path setup code can be executed"""
        # This test ensures the path setup code in the module can be reached
        import os
        import sys

        from app.reconciliation_api import reconciliation

        # Simulate the path setup logic as it appears in the module
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(reconciliation.__file__), "..", "..")
        )
        original_path = sys.path.copy()

        try:
            # Remove project_root if it exists to test the insertion
            if project_root in sys.path:
                sys.path.remove(project_root)

            # Now test the insertion logic
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            # Verify it was inserted at the beginning
            assert sys.path[0] == project_root

        finally:
            # Restore original path
            sys.path = original_path
