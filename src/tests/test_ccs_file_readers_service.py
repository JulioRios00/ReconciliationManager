import json
import os
from collections import defaultdict
from datetime import date, datetime
from unittest.mock import MagicMock, Mock, mock_open, patch

import numpy as np
import pandas as pd
import pytest

from services.ccs_file_readers_service import (
    FileReadersService,
    format_date,
    group_data_by_class,
    save_json,
)


class TestFileReadersService:
    """Test cases for FileReadersService"""

    @pytest.fixture
    def mock_session(self):
        """Mock database session"""
        return Mock()

    @pytest.fixture
    def service(self, mock_session):
        """Create FileReadersService instance with mocked dependencies"""
        with patch(
            "services.ccs_file_readers_service.CateringInvoiceRepository"
        ) as mock_catering_repo, patch(
            "services.ccs_file_readers_service.AirCompanyInvoiceRepository"
        ) as mock_air_repo, patch(
            "services.ccs_file_readers_service.FlightClassMappingRepository"
        ) as mock_flight_class_repo, patch(
            "services.ccs_file_readers_service.FlightNumberMappingRepository"
        ) as mock_flight_num_repo:

            mock_catering_repo.return_value = Mock()
            mock_air_repo.return_value = Mock()
            mock_flight_class_repo.return_value = Mock()
            mock_flight_num_repo.return_value = Mock()

            service = FileReadersService(mock_session)

            return service

    def test_init(self, mock_session):
        """Test FileReadersService initialization"""
        with patch(
            "services.ccs_file_readers_service.CateringInvoiceRepository"
        ) as mock_catering_repo, patch(
            "services.ccs_file_readers_service.AirCompanyInvoiceRepository"
        ) as mock_air_repo, patch(
            "services.ccs_file_readers_service.FlightClassMappingRepository"
        ) as mock_flight_class_repo, patch(
            "services.ccs_file_readers_service.FlightNumberMappingRepository"
        ) as mock_flight_num_repo:

            service = FileReadersService(mock_session)

            mock_catering_repo.assert_called_once_with(mock_session)
            mock_air_repo.assert_called_once_with(mock_session)
            mock_flight_class_repo.assert_called_once_with(mock_session)
            mock_flight_num_repo.assert_called_once_with(mock_session)

            assert service.session == mock_session

    @patch("pandas.read_excel")
    def test_billing_inflair_invoice_report_success(self, mock_read_excel, service):
        """Test successful billing inflair invoice report reading"""
        # Create a more realistic mock DataFrame
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=10)  # Mock len() operation

        # Mock column access and operations
        mock_number_series = Mock()
        mock_number_series.astype = Mock(return_value=Mock())
        mock_number_series.astype.return_value.str.contains = Mock(
            return_value=[False, False, False]
        )

        mock_df.__getitem__ = Mock(return_value=mock_number_series)
        mock_df.__setitem__ = Mock()
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.select_dtypes = Mock(return_value=Mock(columns=["col1", "col2"]))
        mock_df.to_dict = Mock(return_value=[{"test": "data"}])

        mock_read_excel.return_value = mock_df

        result = service.billing_inflair_invoice_report("/path/to/file.xlsx")

        mock_read_excel.assert_called_once_with(
            "/path/to/file.xlsx", skiprows=12, header=None
        )
        assert result == [{"test": "data"}]

    @patch("pandas.read_excel")
    def test_billing_inflair_invoice_report_with_date_conversion(
        self, mock_read_excel, service
    ):
        """Test billing inflair invoice report with date column conversion"""
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=10)
        mock_df.columns = ["FlightDate", "InvoiceDate", "PaidDate", "Number"]

        # Mock column access with proper boolean series for filtering
        mock_number_series = Mock()
        mock_number_series.astype = Mock(return_value=Mock())
        mock_number_series.astype.return_value.str.contains = Mock(
            return_value=[False, False, False]
        )

        def mock_getitem(key):
            if key == "Number":
                return mock_number_series
            else:
                return Mock()

        mock_df.__getitem__ = Mock(side_effect=mock_getitem)
        mock_df.__setitem__ = Mock()
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.select_dtypes = Mock(return_value=Mock(columns=["col1"]))
        mock_df.to_dict = Mock(return_value=[{"FlightDate": date(2023, 1, 1)}])

        mock_read_excel.return_value = mock_df

        with patch("pandas.to_datetime") as mock_to_datetime, patch(
            "pandas.notnull", return_value=[True, True, True]
        ):

            mock_to_datetime.return_value.dt.date = date(2023, 1, 1)

            result = service.billing_inflair_invoice_report("/path/to/file.xlsx")

            assert result == [{"FlightDate": date(2023, 1, 1)}]

    @patch("pandas.read_excel")
    def test_billing_promeus_invoice_report_success(self, mock_read_excel, service):
        """Test successful billing promeus invoice report reading"""
        # Create mock DataFrame with expected columns
        mock_df = Mock()
        mock_df.columns = [
            "SUPPLIER",
            "FLIGHT DATE",
            "FLIGHT NO.",
            "DEP",
            "ARR",
            "CLASS",
        ]
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.reset_index = Mock(return_value=mock_df)
        mock_df.rename = Mock(return_value=mock_df)
        mock_df.__contains__ = Mock(return_value=True)
        mock_df.__getitem__ = Mock(return_value=Mock())
        mock_df.__setitem__ = Mock()
        mock_df.select_dtypes = Mock(return_value=Mock(columns=["col1"]))
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.to_dict = Mock(return_value=[{"test": "data"}])

        mock_read_excel.return_value = mock_df

        result = service.billing_promeus_invoice_report("/path/to/file.xlsx")

        mock_read_excel.assert_called_once_with("/path/to/file.xlsx", header=0)
        assert result is None  # Method doesn't return data, just inserts to DB

    @patch("pandas.read_excel")
    def test_billing_promeus_invoice_report_missing_columns(
        self, mock_read_excel, service
    ):
        """Test billing promeus invoice report with missing required columns"""
        mock_df = Mock()
        mock_df.columns = ["WRONG_COL1", "WRONG_COL2"]  # Missing required columns

        mock_read_excel.return_value = mock_df

        with pytest.raises(ValueError, match="Please share the correct file"):
            service.billing_promeus_invoice_report("/path/to/file.xlsx")

    @patch("pandas.read_excel")
    def test_billing_promeus_invoice_report_db_insertion_success(
        self, mock_read_excel, service
    ):
        """Test successful database insertion in billing promeus invoice report"""
        mock_df = Mock()
        mock_df.columns = [
            "SUPPLIER",
            "FLIGHT DATE",
            "FLIGHT NO.",
            "DEP",
            "ARR",
            "CLASS",
        ]
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.reset_index = Mock(return_value=mock_df)
        mock_df.rename = Mock(return_value=mock_df)
        mock_df.__contains__ = Mock(return_value=True)
        mock_df.__getitem__ = Mock(return_value=Mock())
        mock_df.__setitem__ = Mock()
        mock_df.select_dtypes = Mock(return_value=Mock(columns=[]))
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.to_dict = Mock(return_value=[{"test": "data"}])

        mock_read_excel.return_value = mock_df

        # Mock successful DB insertion
        service.air_company_invoice_repository.insert_air_company_invoice = Mock()

        service.billing_promeus_invoice_report("/path/to/file.xlsx")

        service.air_company_invoice_repository.insert_air_company_invoice.assert_called_once_with(
            [{"test": "data"}]
        )

    @patch("pandas.read_excel")
    def test_billing_promeus_invoice_report_db_insertion_error(
        self, mock_read_excel, service
    ):
        """Test database insertion error handling in billing promeus invoice report"""
        mock_df = Mock()
        mock_df.columns = [
            "SUPPLIER",
            "FLIGHT DATE",
            "FLIGHT NO.",
            "DEP",
            "ARR",
            "CLASS",
        ]
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.reset_index = Mock(return_value=mock_df)
        mock_df.rename = Mock(return_value=mock_df)
        mock_df.__contains__ = Mock(return_value=True)
        mock_df.__getitem__ = Mock(return_value=Mock())
        mock_df.__setitem__ = Mock()
        mock_df.select_dtypes = Mock(return_value=Mock(columns=[]))
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.to_dict = Mock(return_value=[{"test": "data"}])

        mock_read_excel.return_value = mock_df

        # Mock DB insertion error
        service.air_company_invoice_repository.insert_air_company_invoice = Mock(
            side_effect=Exception("DB Error")
        )

        # Should not raise exception, just print error
        service.billing_promeus_invoice_report("/path/to/file.xlsx")

    @patch("os.path.splitext")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="Facility,Data\nRow1,Value1\nRow2,Value2",
    )
    @patch("pandas.read_csv")
    def test_billing_inflair_recon_report_csv_success(
        self, mock_read_csv, mock_file, mock_splitext, service
    ):
        """Test successful CSV billing inflair recon report reading"""
        mock_splitext.return_value = ("/path/to/file", ".csv")

        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=5)  # Mock len() to return > 2
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.iloc = Mock(return_value=mock_df)
        mock_df.columns = ["Facility", "Flt Date", "Flt No."]
        mock_df.rename = Mock(return_value=mock_df)
        mock_df.__contains__ = Mock(return_value=True)
        mock_df.__getitem__ = Mock(return_value=Mock())
        mock_df.__setitem__ = Mock()
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.to_dict = Mock(
            return_value=[{"facility": "Test", "flt_date": "2023-01-01"}]
        )

        mock_read_csv.return_value = mock_df

        result = service.billing_inflair_recon_report("/path/to/file.csv")

        mock_read_csv.assert_called_once()
        assert result == [{"facility": "Test", "flt_date": "2023-01-01"}]

    @patch("os.path.splitext")
    @patch("pandas.read_excel")
    def test_billing_inflair_recon_report_excel_success(
        self, mock_read_excel, mock_splitext, service
    ):
        """Test successful Excel billing inflair recon report reading"""
        mock_splitext.return_value = ("/path/to/file", ".xlsx")

        # Mock for header detection
        mock_df_temp = Mock()
        mock_df_temp.iterrows = Mock(return_value=[(0, Mock())])
        mock_df_temp.iterrows.return_value[0][1].__getitem__ = Mock(
            return_value="Facility"
        )

        # Mock for main data reading
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=5)  # Mock len() to return > 2
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.iloc = Mock(return_value=mock_df)
        mock_df.columns = ["Facility", "Flt Date", "Flt No."]
        mock_df.rename = Mock(return_value=mock_df)
        mock_df.__contains__ = Mock(return_value=True)
        mock_df.__getitem__ = Mock(return_value=Mock())
        mock_df.__setitem__ = Mock()
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.to_dict = Mock(return_value=[{"facility": "Test"}])

        mock_read_excel.side_effect = [mock_df_temp, mock_df]

        result = service.billing_inflair_recon_report("/path/to/file.xlsx")

        assert len(mock_read_excel.call_args_list) == 2
        assert result == [{"facility": "Test"}]

    @patch("os.path.splitext")
    def test_billing_inflair_recon_report_unsupported_format(
        self, mock_splitext, service
    ):
        """Test billing inflair recon report with unsupported file format"""
        mock_splitext.return_value = ("/path/to/file", ".txt")

        with pytest.raises(ValueError, match="Unsupported file format"):
            service.billing_inflair_recon_report("/path/to/file.txt")

    @patch("pandas.read_excel")
    def test_billing_inflair_recon_report_db_insertion_success(
        self, mock_read_excel, service
    ):
        """Test successful database insertion in billing inflair recon report"""
        # Mock file reading
        with patch("os.path.splitext", return_value=("/path/to/file", ".xlsx")), patch(
            "pandas.read_excel"
        ) as mock_read_excel:

            mock_df_temp = Mock()
            mock_df_temp.iterrows = Mock(return_value=[(0, Mock())])
            mock_df_temp.iterrows.return_value[0][1].__getitem__ = Mock(
                return_value="Facility"
            )

            mock_df = Mock()
            mock_df.__len__ = Mock(return_value=5)  # Mock len() to return > 2
            mock_df.dropna = Mock(return_value=mock_df)
            mock_df.iloc = Mock(return_value=mock_df)
            mock_df.columns = ["Facility", "Flt Date", "Flt No."]
            mock_df.rename = Mock(return_value=mock_df)
            mock_df.__contains__ = Mock(return_value=True)
            mock_df.__getitem__ = Mock(return_value=Mock())
            mock_df.__setitem__ = Mock()
            mock_df.replace = Mock(return_value=mock_df)
            mock_df.to_dict = Mock(return_value=[{"facility": "Test"}])

            mock_read_excel.side_effect = [mock_df_temp, mock_df]

            # Mock successful DB insertion
            service.catering_invoice_repository.bulk_insert = Mock()

            result = service.billing_inflair_recon_report("/path/to/file.xlsx")

            service.catering_invoice_repository.bulk_insert.assert_called_once()

    @patch("pandas.read_excel")
    def test_pricing_read_inflair_success(self, mock_read_excel, service):
        """Test successful pricing read inflair"""
        mock_df = Mock()
        mock_df.columns = ["id", "airline_code", "item_code", "start_date", "end_date"]

        # Mock DataFrame operations
        mock_id_series = Mock()
        mock_id_series.astype = Mock(return_value=Mock())
        mock_id_series.astype.return_value.str.match = Mock(
            return_value=[False, False, False]
        )

        mock_item_code_series = Mock()

        def mock_getitem(key):
            if key == "id":
                return mock_id_series
            elif key == "item_code":
                return mock_item_code_series
            else:
                return Mock()

        mock_df.__getitem__ = Mock(side_effect=mock_getitem)
        mock_df.__setitem__ = Mock()
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.to_dict = Mock(return_value=[{"item_code": "TEST123", "price": 100.50}])

        mock_read_excel.return_value = mock_df

        result = service.pricing_read_inflair("/path/to/file.xlsx")

        mock_read_excel.assert_called_once_with("/path/to/file.xlsx", skiprows=8)
        assert result == [{"item_code": "TEST123", "price": 100.50}]

    @patch("pandas.read_excel")
    def test_pricing_read_promeus_with_flight_classes_success(
        self, mock_read_excel, service
    ):
        """Test successful pricing read promeus with flight classes"""
        # Create mock DataFrame with iterrows
        mock_df = Mock()
        mock_row_data = {
            0: "Business Class",
            2: "Service Code",
            3: "Description",
            4: "USD",
            5: 150.00,
        }
        mock_row = Mock()
        mock_row.__getitem__ = Mock(side_effect=lambda key: mock_row_data.get(key))

        mock_df.iterrows = Mock(
            return_value=[
                (0, mock_row),  # Class header
                (1, Mock()),  # Data row
            ]
        )

        # Mock DataFrame operations for flight class filtering
        mock_flight_class_series = Mock()
        mock_flight_class_series.str = Mock()
        mock_flight_class_series.str.contains = Mock(return_value=[True, False, True])

        mock_price_series = Mock()
        mock_valid_from_series = Mock()
        mock_valid_to_series = Mock()

        def mock_getitem(key):
            if key == "flight_class":
                return mock_flight_class_series
            elif key == "price":
                return mock_price_series
            elif key == "valid_from":
                return mock_valid_from_series
            elif key == "valid_to":
                return mock_valid_to_series
            else:
                return Mock()

        mock_df.__getitem__ = Mock(side_effect=mock_getitem)
        mock_df.__setitem__ = Mock()
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.to_dict = Mock(return_value=[{"flight_class": "Y", "price": 200.00}])

        mock_read_excel.return_value = mock_df

        result = service.pricing_read_promeus_with_flight_classes("/path/to/file.xlsx")

        mock_read_excel.assert_called_once_with("/path/to/file.xlsx", skiprows=8)
        assert result == [{"flight_class": "Y", "price": 200.00}]

        result = service.pricing_read_promeus_with_flight_classes("/path/to/file.xlsx")

        mock_read_excel.assert_called_once_with(
            "/path/to/file.xlsx",
            sheet_name="Price History Report",
            engine="openpyxl",
            header=None,
        )
        assert isinstance(result, list)

    @patch("pandas.read_excel")
    def test_read_flight_class_mapping_success(self, mock_read_excel, service):
        """Test successful flight class mapping reading"""
        mock_df = Mock()
        mock_df.columns = ["Class", "Inflair Class", "Item Group"]

        # Mock DataFrame operations
        mock_class_series = Mock()
        mock_inflair_class_series = Mock()
        mock_item_group_series = Mock()

        def mock_getitem(key):
            if key == "Class":
                return mock_class_series
            elif key == "Inflair Class":
                return mock_inflair_class_series
            elif key == "Item Group":
                return mock_item_group_series
            else:
                return Mock()

        mock_df.__getitem__ = Mock(side_effect=mock_getitem)
        mock_df.__setitem__ = Mock()
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.reset_index = Mock(return_value=mock_df)
        mock_df.rename = Mock(return_value=mock_df)
        mock_df.select_dtypes = Mock(return_value=Mock(columns=["Class"]))
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.to_dict = Mock(
            return_value=[{"promeus_class": "Y", "inflair_class": "Economy"}]
        )

        mock_read_excel.return_value = mock_df

        result = service.read_flight_class_mapping("/path/to/file.xlsx")

        mock_read_excel.assert_called_once_with(
            "/path/to/file.xlsx", sheet_name=0, engine="openpyxl"
        )
        assert result == [{"promeus_class": "Y", "inflair_class": "Economy"}]

    @patch("pandas.read_excel")
    def test_read_flight_class_mapping_db_insertion_success(
        self, mock_read_excel, service
    ):
        """Test successful database insertion in flight class mapping"""
        mock_df = Mock()
        mock_df.columns = ["Class", "Inflair Class", "Item Group"]
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.reset_index = Mock(return_value=mock_df)
        mock_df.rename = Mock(return_value=mock_df)
        mock_df.select_dtypes = Mock(return_value=Mock(columns=[]))
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.to_dict = Mock(return_value=[{"promeus_class": "Y"}])

        mock_read_excel.return_value = mock_df

        # Mock successful DB insertion
        service.flight_class_mapping_repository.bulk_insert = Mock()

        result = service.read_flight_class_mapping("/path/to/file.xlsx")

        service.flight_class_mapping_repository.bulk_insert.assert_called_once()

    @patch("pandas.read_excel")
    def test_read_flight_number_mapping_success(self, mock_read_excel, service):
        """Test successful flight number mapping reading"""
        mock_df = Mock()
        mock_df.columns = ["Promeus Code", "Inflair Code"]

        # Mock DataFrame operations
        mock_promeus_code_series = Mock()
        mock_inflair_code_series = Mock()

        def mock_getitem(key):
            if key == "Promeus Code":
                return mock_promeus_code_series
            elif key == "Inflair Code":
                return mock_inflair_code_series
            else:
                return Mock()

        mock_df.__getitem__ = Mock(side_effect=mock_getitem)
        mock_df.__setitem__ = Mock()
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.reset_index = Mock(return_value=mock_df)
        mock_df.rename = Mock(return_value=mock_df)
        mock_df.__contains__ = Mock(return_value=True)
        mock_df.select_dtypes = Mock(return_value=Mock(columns=[]))
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.to_dict = Mock(
            return_value=[
                {
                    "air_company_flight_number": "AB123",
                    "catering_flight_number": "CD456",
                }
            ]
        )

        mock_read_excel.return_value = mock_df

        result = service.read_flight_number_mapping("/path/to/file.xlsx")

        mock_read_excel.assert_called_once_with(
            "/path/to/file.xlsx", sheet_name=0, engine="openpyxl"
        )
        assert result == [
            {"air_company_flight_number": "AB123", "catering_flight_number": "CD456"}
        ]

    @patch("pandas.read_excel")
    def test_read_flight_number_mapping_missing_columns(self, mock_read_excel, service):
        """Test flight number mapping with missing expected columns"""
        mock_df = Mock()
        mock_df.columns = ["Wrong Column 1", "Wrong Column 2"]
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.reset_index = Mock(return_value=mock_df)
        mock_df.rename = Mock(return_value=mock_df)
        mock_df.__contains__ = Mock(return_value=False)

        mock_read_excel.return_value = mock_df

        with pytest.raises(ValueError, match="No expected columns found"):
            service.read_flight_number_mapping("/path/to/file.xlsx")

    @patch("pandas.read_excel")
    def test_read_flight_number_mapping_db_insertion_success(
        self, mock_read_excel, service
    ):
        """Test successful database insertion in flight number mapping"""
        mock_df = Mock()
        mock_df.columns = ["Promeus Code", "Inflair Code"]
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.reset_index = Mock(return_value=mock_df)
        mock_df.rename = Mock(return_value=mock_df)
        mock_df.__contains__ = Mock(return_value=True)
        mock_df.__getitem__ = Mock(return_value=Mock())
        mock_df.__setitem__ = Mock()
        mock_df.select_dtypes = Mock(return_value=Mock(columns=[]))
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.to_dict = Mock(return_value=[{"air_company_flight_number": "AB123"}])

        mock_read_excel.return_value = mock_df

        # Mock successful DB insertion
        service.flight_number_mapping_repository.bulk_insert = Mock()

        result = service.read_flight_number_mapping("/path/to/file.xlsx")

        service.flight_number_mapping_repository.bulk_insert.assert_called_once()


class TestUtilityFunctions:
    """Test cases for utility functions"""

    def test_format_date_with_timestamp(self):
        """Test format_date with pandas Timestamp"""
        timestamp = pd.Timestamp("2023-01-15")
        result = format_date(timestamp)
        assert result == date(2023, 1, 15)

    def test_format_date_with_date_object(self):
        """Test format_date with date object"""
        date_obj = date(2023, 1, 15)
        result = format_date(date_obj)
        assert result == date(2023, 1, 15)

    def test_format_date_with_string_dmY(self):
        """Test format_date with string in D/M/YYYY format"""
        date_str = "15/01/2023"
        result = format_date(date_str)
        assert result == date(2023, 1, 15)

    def test_format_date_with_string_dmy(self):
        """Test format_date with string in D/M/YY format"""
        date_str = "15/01/23"
        result = format_date(date_str)
        assert result == date(2023, 1, 15)

    def test_format_date_with_invalid_string(self):
        """Test format_date with invalid string"""
        date_str = "invalid-date"
        result = format_date(date_str)
        assert result is None

    def test_format_date_with_none(self):
        """Test format_date with None value"""
        result = format_date(None)
        assert result is None

    def test_format_date_with_empty_string(self):
        """Test format_date with empty string"""
        result = format_date("")
        assert result is None

    def test_group_data_by_class_success(self):
        """Test successful data grouping by class"""
        data = [
            {"class": "Business", "facility": "JFK", "price": 100},
            {"class": "Business", "facility": "LAX", "price": 120},
            {"class": "Economy", "facility": "JFK", "price": 50},
            {"class": None, "facility": "ORD", "price": 75},  # Should be skipped
            {
                "class": "Business",
                "facility": "Facility",
                "price": 90,
            },  # Should be skipped
        ]

        result = group_data_by_class(data)

        expected = {
            "Business": [
                {"facility": "JFK", "price": 100},
                {"facility": "LAX", "price": 120},
            ],
            "Economy": [{"facility": "JFK", "price": 50}],
        }

        assert result == expected

    def test_group_data_by_class_empty_data(self):
        """Test grouping with empty data"""
        result = group_data_by_class([])
        assert result == {}

    def test_group_data_by_class_no_valid_data(self):
        """Test grouping with no valid data"""
        data = [
            {"class": None, "facility": "JFK"},
            {"class": "Business", "facility": "Facility"},
            {"facility": "ORD"},  # Missing class
        ]

        result = group_data_by_class(data)
        assert result == {}

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_json_success(self, mock_json_dump, mock_file):
        """Test successful JSON saving"""
        data = [{"test": "data"}]
        output_path = "/path/to/output.json"

        save_json(data, output_path)

        mock_file.assert_called_once_with(output_path, "w", encoding="utf-8")
        mock_json_dump.assert_called_once_with(
            data, mock_file(), ensure_ascii=False, indent=4
        )


class TestErrorHandling:
    """Test cases for error handling scenarios"""

    @pytest.fixture
    def service(self):
        """Create service instance for error testing"""
        mock_session = Mock()
        with patch(
            "services.ccs_file_readers_service.CateringInvoiceRepository"
        ), patch(
            "services.ccs_file_readers_service.AirCompanyInvoiceRepository"
        ), patch(
            "services.ccs_file_readers_service.FlightClassMappingRepository"
        ), patch(
            "services.ccs_file_readers_service.FlightNumberMappingRepository"
        ):
            return FileReadersService(mock_session)

    @patch("pandas.read_excel")
    def test_billing_inflair_recon_report_csv_read_error(
        self, mock_read_excel, service
    ):
        """Test CSV read error handling"""
        with patch("os.path.splitext", return_value=("/path/to/file", ".csv")), patch(
            "builtins.open", side_effect=IOError("File not found")
        ):

            # Should handle the error gracefully
            result = service.billing_inflair_recon_report("/path/to/file.csv")
            assert result == []

    @patch("pandas.read_excel")
    def test_read_flight_class_mapping_excel_error(self, mock_read_excel, service):
        """Test Excel read error handling in flight class mapping"""
        mock_read_excel.side_effect = Exception("Excel read error")

        result = service.read_flight_class_mapping("/path/to/file.xlsx")

        assert result == []

    @patch("pandas.read_excel")
    def test_read_flight_number_mapping_excel_error(self, mock_read_excel, service):
        """Test Excel read error handling in flight number mapping"""
        mock_read_excel.side_effect = Exception("Excel read error")

        result = service.read_flight_number_mapping("/path/to/file.xlsx")

        assert result == []

    @patch("pandas.read_excel")
    def test_billing_inflair_recon_report_db_insertion_error(
        self, mock_read_excel, service
    ):
        """Test database insertion error handling in billing inflair recon report"""
        with patch("os.path.splitext", return_value=("/path/to/file", ".xlsx")), patch(
            "pandas.read_excel"
        ) as mock_read_excel:

            # Mock successful file reading
            mock_df_temp = Mock()
            mock_df_temp.iterrows = Mock(return_value=[(0, Mock())])
            mock_df_temp.iterrows.return_value[0][1].__getitem__ = Mock(
                return_value="Facility"
            )

            mock_df = Mock()
            mock_df.dropna = Mock(return_value=mock_df)
            mock_df.iloc = Mock(return_value=mock_df)
            mock_df.columns = ["Facility"]
            mock_df.rename = Mock(return_value=mock_df)
            mock_df.__contains__ = Mock(return_value=True)
            mock_df.__getitem__ = Mock(return_value=Mock())
            mock_df.__setitem__ = Mock()
            mock_df.replace = Mock(return_value=mock_df)
            mock_df.to_dict = Mock(return_value=[{"facility": "Test"}])

            mock_read_excel.side_effect = [mock_df_temp, mock_df]

            # Mock DB insertion error
            service.catering_invoice_repository.bulk_insert = Mock(
                side_effect=Exception("DB Error")
            )

            # Should not raise exception
            result = service.billing_inflair_recon_report("/path/to/file.xlsx")
            assert result == [{"facility": "Test"}]

    @patch("pandas.read_excel")
    def test_read_flight_class_mapping_db_insertion_error(
        self, mock_read_excel, service
    ):
        """Test database insertion error handling in flight class mapping"""
        mock_df = Mock()
        mock_df.columns = ["Class", "Inflair Class"]
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.reset_index = Mock(return_value=mock_df)
        mock_df.rename = Mock(return_value=mock_df)
        mock_df.select_dtypes = Mock(return_value=Mock(columns=[]))
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.to_dict = Mock(return_value=[{"promeus_class": "Y"}])

        mock_read_excel.return_value = mock_df

        # Mock DB insertion error
        service.flight_class_mapping_repository.bulk_insert = Mock(
            side_effect=Exception("DB Error")
        )

        # Should not raise exception
        result = service.read_flight_class_mapping("/path/to/file.xlsx")
        assert result == [{"promeus_class": "Y"}]

    @patch("pandas.read_excel")
    def test_read_flight_number_mapping_db_insertion_error(
        self, mock_read_excel, service
    ):
        """Test database insertion error handling in flight number mapping"""
        mock_df = Mock()
        mock_df.columns = ["Promeus Code", "Inflair Code"]
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.reset_index = Mock(return_value=mock_df)
        mock_df.rename = Mock(return_value=mock_df)
        mock_df.__contains__ = Mock(return_value=True)
        mock_df.__getitem__ = Mock(return_value=Mock())
        mock_df.__setitem__ = Mock()
        mock_df.select_dtypes = Mock(return_value=Mock(columns=[]))
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.to_dict = Mock(return_value=[{"air_company_flight_number": "AB123"}])

        mock_read_excel.return_value = mock_df

        # Mock DB insertion error
        service.flight_number_mapping_repository.bulk_insert = Mock(
            side_effect=Exception("DB Error")
        )

        # Should not raise exception
        result = service.read_flight_number_mapping("/path/to/file.xlsx")
        assert result == [{"air_company_flight_number": "AB123"}]
