import traceback
from datetime import datetime
from repositories.ccs_repository import ReconciliationRepository


class ReconciliationService:
    def __init__(self, db_session):
        self.session = db_session
        self.reconciliation_repository = ReconciliationRepository(db_session)

    def _parse_date(self, date_str):
        """Parse date string to datetime object"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").date()
            except ValueError:
                return None

    def get_all_reconciliation_data(self):
        """Retrieve all data from the ccs.Reconciliation table using SQLAlchemy"""
        try:
            records = self.reconciliation_repository.get_all()
            result_list = [record.serialize() for record in records]
            return {"data": result_list}
        except Exception as e:
            error_details = traceback.format_exc()
            return {
                "message": "Failed to retrieve reconciliation data", 
                "error": str(e)
            }, 501

    def get_paginated_reconciliation_data(
        self,
        limit=100,
        offset=0,
        filter_type='all',
        start_date=None,
        end_date=None,
        flight_number=None,
        item_name=None
    ):
        """Retrieve paginated data from the ccs.Reconciliation table using SQLAlchemy"""
        try:
            # Parse dates if provided
            parsed_start_date = self._parse_date(start_date) if start_date else None
            parsed_end_date = self._parse_date(end_date) if end_date else None

            # Handle different filtering scenarios
            if parsed_start_date and parsed_end_date and flight_number and item_name:
                # Date range + flight number + item name filtering (complex scenario)
                if filter_type == 'all':
                    records = self.reconciliation_repository.get_by_date_range(
                        parsed_start_date, parsed_end_date, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_count_by_date_range(
                        parsed_start_date, parsed_end_date
                    )
                else:
                    records = self.reconciliation_repository.get_filtered_by_date_range(
                        filter_type, parsed_start_date, parsed_end_date, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_filtered_count_by_date_range(
                        filter_type, parsed_start_date, parsed_end_date
                    )
            elif parsed_start_date and parsed_end_date and item_name:
                # Date range + item name filtering
                if filter_type == 'all':
                    records = self.reconciliation_repository.get_by_item_name_and_date_range(
                        item_name, parsed_start_date, parsed_end_date, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_count_by_item_name_and_date_range(
                        item_name, parsed_start_date, parsed_end_date
                    )
                else:
                    # For filtered + date + item, we'll use the basic date range filter for now
                    records = self.reconciliation_repository.get_filtered_by_date_range(
                        filter_type, parsed_start_date, parsed_end_date, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_filtered_count_by_date_range(
                        filter_type, parsed_start_date, parsed_end_date
                    )
            elif flight_number and item_name:
                # Flight number + item name filtering
                if filter_type == 'all':
                    records = self.reconciliation_repository.get_by_item_name_and_flight_number(
                        item_name, flight_number, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_count_by_item_name_and_flight_number(
                        item_name, flight_number
                    )
                else:
                    # For filtered + flight + item, we'll use the basic flight filter for now
                    records = self.reconciliation_repository.get_filtered_by_flight_number(
                        filter_type, flight_number, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_filtered_count_by_flight_number(
                        filter_type, flight_number
                    )
            elif parsed_start_date and parsed_end_date:
                # Date range filtering only
                if filter_type == 'all':
                    records = self.reconciliation_repository.get_by_date_range(
                        parsed_start_date, parsed_end_date, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_count_by_date_range(
                        parsed_start_date, parsed_end_date
                    )
                else:
                    records = self.reconciliation_repository.get_filtered_by_date_range(
                        filter_type, parsed_start_date, parsed_end_date, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_filtered_count_by_date_range(
                        filter_type, parsed_start_date, parsed_end_date
                    )
            elif flight_number:
                # Flight number filtering only
                if filter_type == 'all':
                    records = self.reconciliation_repository.get_by_flight_number(
                        flight_number, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_count_by_flight_number(
                        flight_number
                    )
                else:
                    records = self.reconciliation_repository.get_filtered_by_flight_number(
                        filter_type, flight_number, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_filtered_count_by_flight_number(
                        filter_type, flight_number
                    )
            elif item_name:
                # Item name filtering only
                if filter_type == 'all':
                    records = self.reconciliation_repository.get_by_item_name(
                        item_name, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_count_by_item_name(
                        item_name
                    )
                else:
                    records = self.reconciliation_repository.get_filtered_by_item_name(
                        filter_type, item_name, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_filtered_count_by_item_name(
                        filter_type, item_name
                    )
            else:
                # No filtering
                if filter_type == 'all':
                    records = self.reconciliation_repository.get_paginated(limit, offset)
                    total_count = self.reconciliation_repository.get_count()
                else:
                    records = self.reconciliation_repository.get_filtered_paginated(
                        filter_type, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_filtered_count(filter_type)

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
                    "end_date": end_date,
                    "flight_number": flight_number,
                    "item_name": item_name
                }
            }
        except Exception as e:
            error_details = traceback.format_exc()
            return {
                "message": "Failed to retrieve reconciliation data", 
                "error": str(e)
            }, 501

    def get_reconciliation_summary(self):
        """Get summary statistics for the reconciliation data using SQLAlchemy"""
        try:
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
                }
            }
        except Exception as e:
            error_details = traceback.format_exc()
            return {
                "message": "Failed to retrieve reconciliation summary",
                "error": str(e)
            }, 501
