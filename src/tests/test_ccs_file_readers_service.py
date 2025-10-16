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


class MockDataFrame(Mock):
    """Custom Mock that allows column assignment to work with tolist()"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._columns = None

        # Create a proper iloc indexer mock
        class MockIlocIndexer:
            def __getitem__(self, key):
                return self._df  # iloc[:-2] returns df

        self.iloc = MockIlocIndexer()
        self.iloc._df = self  # Reference back to self

    def __setattr__(self, name, value):
        if name == "columns" and isinstance(value, list):
            # When columns is assigned a list, make it have tolist()
            value = _MockListWithTolist(value)
            super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)

    def rename(self, columns=None, **kwargs):
        if columns:
            new_columns = [columns.get(col, col) for col in self.columns]
            self.columns = _MockListWithTolist(new_columns)
        return self


class SimpleMockDF:
    def __init__(self):
        self.columns = _MockListWithTolist(["Facility", "Flt Date", "Flt No."])
        self.dropna = Mock(return_value=self)
        self.rename = Mock(return_value=self)
        self.replace = Mock(return_value=self)
        self.__contains__ = Mock(return_value=True)
        self.__setitem__ = Mock()
        self.iloc = Mock()
        self.iloc.__getitem__ = Mock(return_value=self)

    def __len__(self):
        return 5

    def __getitem__(self, key):
        return self

    def notna(self):
        return self

    def __setattr__(self, name, value):
        if name == "columns" and isinstance(value, list):
            value = _MockListWithTolist(value)
        super().__setattr__(name, value)

    def rename(self, columns=None, **kwargs):
        if columns:
            new_columns = [columns.get(col, col) for col in self.columns]
            self.columns = _MockListWithTolist(new_columns)
        return self

    def to_dict(self, orient="records"):
        return [{"facility": "Test"}]


class _MockListWithTolist(list):
    """A list that has a tolist() method"""

    def tolist(self):
        return list(self)

    def __contains__(self, item):
        return item in list(self)


class MockSelectDtypesResult:
    def __init__(self):
        self.columns = _MockListWithTolist([])


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
        # Create a mock DataFrame
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=10)
        mock_df.columns = [
            "Number",
            "Date",
            "Date.1",
            "Number.1",
            "F",
            "J",
            "Y",
            "Goods Value",
            "Galley Serv",
            "Total",
            "Statement",
            "Period",
            "Cd",
        ]

        # Mock the Number column to return a series that can be filtered
        mock_number_series = Mock()
        mock_number_series.astype = Mock(return_value=Mock())
        mock_number_series.astype.return_value.str.contains = Mock(
            return_value=pd.Series([True] * 10)
        )

        # Mock df[mask] to return the df itself
        def mock_getitem(key):
            if isinstance(key, str) and key == "Number":
                return mock_number_series
            elif isinstance(key, pd.Series):
                # When df[mask] is called with a boolean series, return df
                return mock_df
            else:
                return Mock()

        mock_df.__getitem__ = Mock(side_effect=mock_getitem)
        mock_df.__setitem__ = Mock()
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.select_dtypes = Mock(return_value=Mock(columns=[]))
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

        # Mock the Number column
        mock_number_series = Mock()
        mock_number_series.astype = Mock(return_value=Mock())
        mock_number_series.astype.return_value.str.contains = Mock(
            return_value=pd.Series([True] * 10)
        )

        def mock_getitem(key):
            if isinstance(key, str) and key == "Number":
                return mock_number_series
            elif isinstance(key, pd.Series):
                return mock_df
            else:
                return Mock()

        mock_df.__getitem__ = Mock(side_effect=mock_getitem)
        mock_df.__setitem__ = Mock()
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.select_dtypes = Mock(return_value=Mock(columns=[]))
        mock_df.to_dict = Mock(return_value=[{"FlightDate": date(2023, 1, 1)}])

        mock_read_excel.return_value = mock_df

        with patch("pandas.to_datetime") as mock_to_datetime, patch(
            "pandas.notnull", return_value=pd.Series([True, True, True])
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

        mock_df = MockDataFrame()
        mock_df.__len__ = Mock(return_value=5)  # Mock len() to return > 2
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.iloc = Mock()
        mock_df.iloc.__getitem__ = Mock(
            return_value=mock_df
        )  # Mock iloc[:-2] to return df

        # Mock columns to behave like pandas Index
        mock_columns = _MockListWithTolist(["Facility", "Flt Date", "Flt No."])
        mock_df.columns = mock_columns

        mock_df.rename = Mock(return_value=mock_df)
        mock_df.__contains__ = Mock(return_value=True)

        def mock_getitem(key):
            if key == "facility":
                mock_series = Mock()
                # Return a mock that behaves like a boolean Series
                mock_bool_series = Mock()
                mock_bool_series.__getitem__ = Mock(return_value=True)  # For indexing
                mock_bool_series.__len__ = Mock(return_value=5)
                mock_series.notna = Mock(return_value=mock_bool_series)
                return mock_series
            elif isinstance(key, Mock):
                # Handle boolean indexing: df[boolean_series]
                return mock_df  # Return the same DataFrame (filtered)
            else:
                return Mock()

        mock_df.__getitem__ = Mock(side_effect=mock_getitem)
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
        mock_row = Mock()
        mock_row.__getitem__ = Mock(return_value="Facility")
        mock_df_temp.iterrows = Mock(return_value=[(0, mock_row)])

        # Mock for main data reading
        mock_df = MockDataFrame()
        mock_df.__len__ = Mock(return_value=5)  # Mock len() to return > 2
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.iloc = Mock()
        mock_df.iloc.__getitem__ = Mock(
            return_value=mock_df
        )  # Mock iloc[:-2] to return df

        # Mock columns to behave like pandas Index
        mock_columns = _MockListWithTolist(["Facility", "Flt Date", "Flt No."])
        mock_df.columns = mock_columns

        mock_df.rename = Mock(return_value=mock_df)
        mock_df.__contains__ = Mock(return_value=True)

        def mock_getitem(key):
            if key == "facility":
                mock_series = Mock()
                # Return a mock that behaves like a boolean Series
                mock_bool_series = Mock()
                mock_bool_series.__getitem__ = Mock(return_value=True)  # For indexing
                mock_bool_series.__len__ = Mock(return_value=5)
                mock_series.notna = Mock(return_value=mock_bool_series)
                return mock_series
            elif isinstance(key, Mock):
                # Handle boolean indexing: df[boolean_series]
                return mock_df  # Return the same DataFrame (filtered)
            else:
                return Mock()

        mock_df.__getitem__ = Mock(side_effect=mock_getitem)
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

            # Mock for header detection
            mock_df_temp = Mock()
            mock_row = Mock()
            mock_row.__getitem__ = Mock(return_value="Facility")
            mock_df_temp.iterrows = Mock(return_value=[(0, mock_row)])

            mock_df = MockDataFrame()
            mock_df.__len__ = Mock(return_value=5)  # Mock len() to return > 2
            mock_df.dropna = Mock(return_value=mock_df)
            # Mock columns to behave like pandas Index
            mock_columns = _MockListWithTolist(["Facility", "Flt Date", "Flt No."])
            mock_df.columns = mock_columns

            mock_df.rename = Mock(return_value=mock_df)
            mock_df.__contains__ = Mock(return_value=True)

            def mock_getitem(key):
                if key == "facility":
                    mock_series = Mock()
                    # Return a mock that behaves like a boolean Series
                    mock_bool_series = Mock()
                    mock_bool_series.__getitem__ = Mock(
                        return_value=True
                    )  # For indexing
                    mock_bool_series.__len__ = Mock(return_value=5)
                    mock_series.notna = Mock(return_value=mock_bool_series)
                    return mock_series
                elif isinstance(key, Mock):
                    # Handle boolean indexing: df[boolean_series]
                    return mock_df  # Return the same DataFrame (filtered)
                else:
                    return Mock()

            mock_df.__getitem__ = Mock(side_effect=mock_getitem)
            mock_df.__setitem__ = Mock()
            mock_df.replace = Mock(return_value=mock_df)
            mock_df.to_dict = Mock(
                return_value=[
                    {
                        "facility": "Test",
                        "flt_date": "2023-01-01",
                        "flt_no": "123",
                        "flt_inv": "INV001",
                        "class_": "A",
                        "item_group": "Food",
                        "itemcode": "F001",
                        "item_desc": "Test Item",
                        "al_bill_code": "ABC",
                        "al_bill_desc": "Test Bill",
                        "bill_catg": "Category",
                        "unit": "kg",
                        "pax": "100",
                        "qty": "50",
                        "unit_price": "10.0",
                        "total_amount": "500.0",
                    }
                ]
            )

            mock_read_excel.side_effect = [mock_df_temp, mock_df]

            # Mock successful DB insertion
            service.catering_invoice_repository.bulk_insert = Mock()

            result = service.billing_inflair_recon_report("/path/to/file.xlsx")

            service.catering_invoice_repository.bulk_insert.assert_called_once()

    @patch("pandas.read_excel")
    @patch("pandas.to_numeric")
    def test_pricing_read_inflair_success(
        self, mock_to_numeric, mock_read_excel, service
    ):
        """Test successful pricing read inflair"""
        mock_df = Mock()
        mock_df.columns = ["id", "airline_code", "item_code", "start_date", "end_date"]

        # Mock DataFrame operations
        mock_id_series = Mock()
        mock_id_series.astype = Mock(return_value=Mock())
        mock_match_result = pd.Series([False, False, False])
        mock_id_series.astype.return_value.str.match = Mock(
            return_value=mock_match_result
        )

        mock_item_code_series = Mock()
        mock_item_code_series.notna = Mock(return_value=pd.Series([True]))

        def mock_getitem(key):
            if isinstance(key, pd.Series) and key.dtype == bool:
                # When df[boolean_series] is called, return the df itself
                return mock_df
            elif isinstance(key, str) and key == "id":
                return mock_id_series
            elif isinstance(key, str) and key == "item_code":
                return mock_item_code_series
            elif isinstance(key, str) and key == "price":
                return Mock(ndim=1)  # Mock Series for price column
            else:
                return Mock()

        mock_df.__getitem__ = Mock(side_effect=mock_getitem)
        mock_df.__setitem__ = Mock()
        mock_df.replace = Mock(return_value=mock_df)
        mock_df.to_dict = Mock(return_value=[{"item_code": "TEST123", "price": 100.50}])

        mock_to_numeric.return_value.round = Mock(return_value=Mock())

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
                (
                    1,
                    Mock(__getitem__=Mock(return_value="Data")),
                ),  # Data row with __getitem__
            ]
        )

        # Mock DataFrame operations for flight class filtering
        mock_flight_class_series = Mock()
        mock_flight_class_series.str = Mock()
        mock_flight_class_series.str.contains = Mock(
            return_value=pd.Series([True, False, True])
        )

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
        mock_df = MockDataFrame()

        # Mock columns to behave like pandas Index
        mock_columns = _MockListWithTolist(["Promeus Code", "Inflair Code"])
        mock_df.columns = mock_columns

        # Create a mock boolean series for filtering
        class MockBooleanSeries:
            """Mock series that supports & and | operations"""

            def __and__(self, other):
                return self

            def __or__(self, other):
                return self

            def __ne__(self, other):
                return self

        mock_boolean_series = MockBooleanSeries()

        # Mock DataFrame operations
        mock_promeus_code_series = Mock()
        mock_inflair_code_series = Mock()

        # Mock series methods
        mock_promeus_code_series.apply = Mock(return_value=mock_promeus_code_series)
        mock_promeus_code_series.astype = Mock(return_value=mock_promeus_code_series)
        mock_promeus_code_series.notna = Mock(return_value=mock_boolean_series)
        mock_promeus_code_series.__ne__ = Mock(return_value=mock_boolean_series)

        mock_inflair_code_series.apply = Mock(return_value=mock_inflair_code_series)
        mock_inflair_code_series.astype = Mock(return_value=mock_inflair_code_series)
        mock_inflair_code_series.notna = Mock(return_value=mock_boolean_series)
        mock_inflair_code_series.__ne__ = Mock(return_value=mock_boolean_series)

        def mock_getitem(key):
            if key == "Promeus Code":
                return mock_promeus_code_series
            elif key == "Inflair Code":
                return mock_inflair_code_series
            elif key == "air_company_flight_number":
                return mock_promeus_code_series
            elif key == "catering_flight_number":
                return mock_inflair_code_series
            elif isinstance(key, list):
                # When selecting columns with a list (df[list_of_columns])
                return mock_df
            elif isinstance(key, MockBooleanSeries):
                # When filtering with a boolean series
                return mock_df
            else:
                return Mock()

        mock_df.__getitem__ = Mock(side_effect=mock_getitem)
        mock_df.__setitem__ = Mock()

        # dropna and reset_index are called with inplace=True, so they return None
        mock_df.dropna = Mock(return_value=None)
        mock_df.reset_index = Mock(return_value=None)
        mock_df.__contains__ = Mock(return_value=True)

        # Fix: Use MockSelectDtypesResult which has an iterable columns attribute
        mock_select_dtypes_result = MockSelectDtypesResult()
        mock_select_dtypes_result.columns = _MockListWithTolist(
            ["air_company_flight_number", "catering_flight_number"]
        )
        mock_df.select_dtypes = Mock(return_value=mock_select_dtypes_result)

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
            "/path/to/file.xlsx", sheet_name=1, engine="openpyxl"
        )
        assert result == [
            {"air_company_flight_number": "AB123", "catering_flight_number": "CD456"}
        ]

    @patch("pandas.read_excel")
    def test_read_flight_number_mapping_missing_columns(self, mock_read_excel, service):
        """Test flight number mapping with missing expected columns"""
        mock_df = Mock()
        mock_df.columns = Mock()  # Mock columns
        mock_df.columns.tolist = Mock(return_value=["Wrong Column 1", "Wrong Column 2"])
        mock_df.columns.__contains__ = Mock(
            return_value=False
        )  # Expected columns not found
        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.reset_index = Mock(return_value=mock_df)
        mock_df.rename = Mock(return_value=mock_df)
        mock_df.__getitem__ = Mock(return_value=Mock())

        mock_read_excel.return_value = mock_df

        result = service.read_flight_number_mapping("/path/to/file.xlsx")

        assert result == []

    @patch("pandas.read_excel")
    def test_read_flight_number_mapping_db_insertion_success(
        self, mock_read_excel, service
    ):
        """Test successful database insertion in flight number mapping"""
        mock_df = MockDataFrame()

        # Mock columns to behave like pandas Index
        mock_columns = _MockListWithTolist(["Promeus Code", "Inflair Code"])
        mock_df.columns = mock_columns

        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.reset_index = Mock(return_value=mock_df)
        mock_df.__contains__ = Mock(return_value=True)

        # Mock the column series for filtering
        mock_air_company_series = Mock()
        mock_air_company_series.notna = Mock(return_value=pd.Series([True]))
        mock_air_company_series.__ne__ = Mock(return_value=pd.Series([True]))

        mock_catering_series = Mock()
        mock_catering_series.notna = Mock(return_value=pd.Series([True]))
        mock_catering_series.__ne__ = Mock(return_value=pd.Series([True]))

        def mock_getitem(key):
            if isinstance(key, str):
                if key == "air_company_flight_number":
                    return mock_air_company_series
                elif key == "catering_flight_number":
                    return mock_catering_series
                else:
                    return Mock()
            else:
                # For boolean indexing like df[boolean_expression]
                return mock_df

        mock_df.__getitem__ = Mock(side_effect=mock_getitem)
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
            "builtins.open", side_effect=OSError("File not found")
        ):

            # Should raise OSError
            with pytest.raises(OSError, match="File not found"):
                service.billing_inflair_recon_report("/path/to/file.csv")

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

            # Mock for header detection
            mock_df_temp = Mock()
            mock_row = Mock()
            mock_row.__getitem__ = Mock(return_value="Facility")
            mock_df_temp.iterrows = Mock(return_value=[(0, mock_row)])

            mock_df = SimpleMockDF()

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
        mock_df = MockDataFrame()

        # Mock columns to behave like pandas Index
        mock_columns = _MockListWithTolist(["Promeus Code", "Inflair Code"])
        mock_df.columns = mock_columns

        mock_df.dropna = Mock(return_value=mock_df)
        mock_df.reset_index = Mock(return_value=mock_df)
        mock_df.__contains__ = Mock(return_value=True)

        # Mock the column series for filtering
        mock_air_company_series = Mock()
        mock_air_company_series.notna = Mock(return_value=pd.Series([True]))
        mock_air_company_series.__ne__ = Mock(return_value=pd.Series([True]))

        mock_catering_series = Mock()
        mock_catering_series.notna = Mock(return_value=pd.Series([True]))
        mock_catering_series.__ne__ = Mock(return_value=pd.Series([True]))

        def mock_getitem(key):
            if isinstance(key, str):
                if key == "air_company_flight_number":
                    return mock_air_company_series
                elif key == "catering_flight_number":
                    return mock_catering_series
                else:
                    return Mock()
            else:
                # For boolean indexing like df[boolean_expression]
                return mock_df

        mock_df.__getitem__ = Mock(side_effect=mock_getitem)
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
