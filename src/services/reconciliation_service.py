import logging
import traceback
from datetime import datetime
from repositories.ccs_repository import ReconciliationRepository


class ReconciliationService:
    def __init__(self, db_session):
        self.session = db_session
        self.reconciliation_repository = ReconciliationRepository(db_session)

    def _parse_date(self, date_str):
        """
        Parse date string to datetime object
        
        Args:
            date_str: Date string in format YYYY-MM-DD
            
        Returns:
            datetime object or None if invalid
        """
        if not date_str:
            return None
            
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
            except ValueError:
                return None

    def get_all_reconciliation_data(self):
        """
        Retrieve all data from the ccs.Reconciliation table using SQLAlchemy

        Returns:
            Dictionary with all reconciliation data
        """
        try:
            records = self.reconciliation_repository.get_all()

            result_list = [record.serialize() for record in records]

            return {"data": result_list}
        except Exception as e:
            error_details = traceback.format_exc()
            logging.error(
                f"Exception in get_all_reconciliation_data: {str(e)}"
                )
            logging.error(f"Traceback: {error_details}")

            return {"message":
                    "Failed to retrieve reconciliation data", "error": str(e)
                    }, 501

    def get_paginated_reconciliation_data(
        self,
        limit=100,
        offset=0,
        filter_type='all',
        start_date=None,
        end_date=None
    ):
        """
        Retrieve paginated data from the
        ccs.Reconciliation table using SQLAlchemy

        Args:
            limit: Number of records to return
            offset: Offset for pagination
            filter_type: Type of filter to apply (
                'all',
                'discrepancies',
                'quantity_difference',
                'price_difference',
                'air_only',
                'cat_only'
                )
            start_date: Start date for date range filter (YYYY-MM-DD format)
            end_date: End date for date range filter (YYYY-MM-DD format)

        Returns:
            Dictionary with paginated reconciliation data and pagination info
        """
        try:
            parsed_start_date = self._parse_date(start_date) if start_date else None
            parsed_end_date = self._parse_date(end_date) if end_date else None

            if (parsed_start_date and parsed_end_date and
                parsed_start_date > parsed_end_date):
                return {
                    "message": "Start date cannot be greater than end date",
                    "error": "Invalid date range"
                }, 400

            if parsed_start_date and parsed_end_date:
                if filter_type == 'all':
                    records = self.reconciliation_repository.get_by_date_range(
                        parsed_start_date, parsed_end_date, limit, offset
                    )
                    total_count = (
                        self.reconciliation_repository.get_count_by_date_range(
                            parsed_start_date, parsed_end_date)
                        )
                else:
                    records = (
                        self.reconciliation_repository
                        .get_filtered_by_date_range(
                            filter_type, parsed_start_date, parsed_end_date,
                            limit, offset)
                        )

                    total_count = (
                        self.reconciliation_repository
                        .get_filtered_count_by_date_range(
                            filter_type, parsed_start_date, parsed_end_date
                        )
                    )
            else:
                if filter_type == 'all':
                    records = self.reconciliation_repository.get_paginated(
                        limit,
                        offset
                        )
                    total_count = self.reconciliation_repository.get_count()
                else:
                    records = (
                        self.reconciliation_repository.get_filtered_paginated(
                            filter_type,
                            limit,
                            offset
                        )
                    )
                    total_count = (
                        self.reconciliation_repository.
                        get_filtered_count(filter_type)
                        )

            result_list = [record.serialize() for record in records]

            return {
                "data": result_list,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "next_offset": (
                        offset + limit if offset + limit < total_count
                        else None
                        )
                },
                "filters": {
                    "filter_type": filter_type,
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
        except Exception as e:
            error_details = traceback.format_exc()
            logging.error(
                f"Exception in get_paginated_reconciliation_data: {str(e)}"
                )
            logging.error(f"Traceback: {error_details}")

            return {"message":
                    "Failed to retrieve reconciliation data", "error": str(e)
                    }, 501

    def get_reconciliation_summary(self, start_date=None, end_date=None):
        """
        Get summary statistics for the reconciliation data using SQLAlchemy

        Args:
            start_date: Optional start date for filtering (YYYY-MM-DD format)
            end_date: Optional end date for filtering (YYYY-MM-DD format)

        Returns:
            Dictionary with summary statistics
        """
        try:
            # Parse dates if provided
            parsed_start_date = self._parse_date(start_date) if start_date else None
            parsed_end_date = self._parse_date(end_date) if end_date else None

            # Get records based on date range
            if parsed_start_date and parsed_end_date:
                records = self.reconciliation_repository.get_by_date_range(
                    parsed_start_date, parsed_end_date
                )
            else:
                records = self.reconciliation_repository.get_all()

            total_records = len(records)
            matching_records = sum(
                1 for r in records if r.Air == 'Yes' and r.Cat == 'Yes'
                )
            air_only_records = sum(
                1 for r in records if r.Air == 'Yes' and r.Cat == 'No'
                )
            cat_only_records = sum(
                1 for r in records if r.Air == 'No' and r.Cat == 'Yes'
                )
            quantity_discrepancies = sum(
                1 for r in records if r.DifQty == 'Yes'
                )
            price_discrepancies = sum(
                1 for r in records if r.DifPrice == 'Yes'
                )
            total_discrepancies = sum(
                1 for r in records if r.DifQty == 'Yes' or r.DifPrice == 'Yes'
                )

            total_amount_difference = 0
            for record in records:
                if record.AmountDif and record.AmountDif.strip():
                    try:
                        total_amount_difference += float(record.AmountDif)
                    except (ValueError, TypeError):
                        pass

            return {
                "summary": {
                    "total_records": total_records,
                    "matching_records": matching_records,
                    "air_only_records": air_only_records,
                    "cat_only_records": cat_only_records,
                    "quantity_discrepancies": quantity_discrepancies,
                    "price_discrepancies": price_discrepancies,
                    "total_discrepancies": total_discrepancies,
                    "total_amount_difference": total_amount_difference
                },
                "filters": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
        except Exception as e:
            error_details = traceback.format_exc()
            logging.error(f"Exception in get_reconciliation_summary: {str(e)}")
            logging.error(f"Traceback: {error_details}")

            return {
                "message": "Failed to retrieve reconciliation summary",
                "error": str(e)
                }, 501
