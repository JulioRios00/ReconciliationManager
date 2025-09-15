from datetime import date
from unittest.mock import MagicMock, Mock

import pytest
from sqlalchemy.orm import Session

from repositories.reconciliation_repository import ReconciliationRepository


class TestReconciliationRepository:
    """Test cases for ReconciliationRepository"""

    @pytest.fixture
    def mock_session(self):
        """Mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance with mocked session"""
        return ReconciliationRepository(mock_session)

    def test_get_all_success(self, repository, mock_session):
        """Test successful retrieval of all records"""
        # Mock query result
        mock_records = [Mock(), Mock()]
        mock_query = Mock()
        mock_query.all.return_value = mock_records
        mock_session.query.return_value = mock_query

        result = repository.get_all()

        assert result == mock_records
        mock_session.query.assert_called_once()

    def test_get_all_exception(self, repository, mock_session):
        """Test exception handling in get_all"""
        mock_session.query.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            repository.get_all()

    def test_get_by_item_name_success(self, repository, mock_session):
        """Test successful retrieval by item name"""
        mock_records = [Mock()]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_records

        mock_session.query.return_value = mock_query

        result = repository.get_by_item_name("test_item", 10, 0)

        assert result == mock_records

    def test_get_count_by_item_name(self, repository, mock_session):
        """Test counting records by item name"""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5

        mock_session.query.return_value = mock_query

        result = repository.get_count_by_item_name("test_item")

        assert result == 5

    def test_get_paginated_success(self, repository, mock_session):
        """Test successful paginated retrieval"""
        mock_records = [Mock(), Mock()]
        mock_query = Mock()
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_records

        mock_session.query.return_value = mock_query

        result = repository.get_paginated(10, 0)

        assert result == mock_records

    def test_get_count_success(self, repository, mock_session):
        """Test successful count retrieval"""
        mock_query = Mock()
        mock_query.count.return_value = 100

        mock_session.query.return_value = mock_query

        result = repository.get_count()

        assert result == 100

    def test_get_by_date_range_success(self, repository, mock_session):
        """Test successful retrieval by date range"""
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 31)
        mock_records = [Mock()]

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_records

        mock_session.query.return_value = mock_query

        result = repository.get_by_date_range(start_date, end_date, 10, 0)

        assert result == mock_records

    def test_get_filtered_by_date_range_success(self, repository, mock_session):
        """Test successful filtered retrieval by date range"""
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 31)
        mock_records = [Mock()]

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_records

        mock_session.query.return_value = mock_query

        result = repository.get_filtered_by_date_range(
            "matched", start_date, end_date, 10, 0
        )

        assert result == mock_records
