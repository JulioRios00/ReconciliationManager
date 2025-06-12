import logging
import traceback
from datetime import datetime
from repositories.ccs_repository import ReconciliationRepository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReconciliationService:
    def __init__(self, db_session):
        self.session = db_session
        self.reconciliation_repository = ReconciliationRepository(db_session)

    def _parse_date(self, date_str):
        """Parse date string to datetime object, handling YYYY-DD-MM format"""
        if not date_str:
            return None

        try:
            # First try standard YYYY-MM-DD format
            parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
            logger.info(f"Parsed date '{date_str}' as standard YYYY-MM-DD to {parsed}")
            return parsed
        except ValueError:
            try:
                # Try YYYY-DD-MM format (your database format)
                parsed_ddmm = datetime.strptime(date_str, "%Y-%d-%m").date()
                logger.info(f"Parsed date '{date_str}' as YYYY-DD-MM to {parsed_ddmm}")
                return parsed_ddmm
            except ValueError:
                try:
                    # Try with datetime string
                    parsed = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").date()
                    logger.info(f"Parsed datetime '{date_str}' to {parsed}")
                    return parsed
                except ValueError:
                    logger.error(f"Could not parse date: {date_str}")
                    return None

    def get_all_reconciliation_data(self):
        """
        Retrieve all data from the ccs.Reconciliation table using SQLAlchemy
        """
        try:
            logger.info("=== get_all_reconciliation_data called ===")
            records = self.reconciliation_repository.get_all()
            logger.info(f"Retrieved {len(records)} total records")

            result_list = [record.serialize() for record in records]

            return {"data": result_list}
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Exception in get_all_reconciliation_data: {str(e)}")
            logger.error(f"Traceback: {error_details}")

            return {
                "message": "Failed to retrieve reconciliation data",
                "error": str(e),
            }, 501

    def get_paginated_reconciliation_data(
        self,
        limit=100,
        offset=0,
        filter_type="all",
        start_date=None,
        end_date=None,
        flight_number=None,  # Add this parameter
    ):
        """
        Retrieve paginated data with detailed logging
        """
        try:
            logger.info(f"=== ReconciliationService called ===")
            logger.info(
                f"Parameters: limit={limit}, offset={offset}, filter_type={filter_type}"
            )
            logger.info(f"Date range: start_date='{start_date}', end_date='{end_date}'")
            logger.info(f"Flight number: flight_number='{flight_number}'")

            parsed_start_date = self._parse_date(start_date) if start_date else None
            parsed_end_date = self._parse_date(end_date) if end_date else None

            logger.info(
                f"Parsed dates: start={parsed_start_date}, end={parsed_end_date}"
            )

            # Handle flight number filtering
            if flight_number:
                logger.info("Applying flight number filter")
                if filter_type == "all":
                    records = (
                        self.reconciliation_repository.get_by_flight_number(
                            flight_number, limit, offset
                        )
                    )
                    total_count = (
                        self.reconciliation_repository
                        .get_count_by_flight_number(
                            flight_number
                        )
                    )
                else:
                    logger.info(
                        "Applying filter_type: "
                        f"{filter_type} with flight number"
                    )
                    records = (
                        self.reconciliation_repository.
                        get_filtered_by_flight_number(
                            filter_type, flight_number, limit, offset
                        )
                    )
                    total_count = (
                        self.reconciliation_repository.
                        get_filtered_count_by_flight_number(
                            filter_type, flight_number
                        )
                    )

                logger.info(
                    f"Flight number query returned {len(records)} "
                    f"records, total_count={total_count}"
                )

            # Handle date range filtering
            elif parsed_start_date and parsed_end_date:
                logger.info("Applying date range filter")
                if filter_type == "all":
                    records = self.reconciliation_repository.get_by_date_range(
                        parsed_start_date, parsed_end_date, limit, offset
                    )
                    total_count = (
                        self.reconciliation_repository.get_count_by_date_range(
                            parsed_start_date, parsed_end_date
                        )
                    )
                else:
                    logger.info(f"Applying filter_type: {filter_type}")
                    records = (
                        self.reconciliation_repository
                        .get_filtered_by_date_range(
                            filter_type,
                            parsed_start_date,
                            parsed_end_date,
                            limit,
                            offset
                        )
                    )
                    total_count = (
                        self.reconciliation_repository
                        .get_filtered_count_by_date_range(
                            filter_type,
                            parsed_start_date,
                            parsed_end_date
                        )
                    )

                logger.info(
                    f"Date range query returned {len(records)} "
                    f"records, total_count={total_count}"
                )
            else:
                logger.info(
                    "No date range or flight number filter,"
                    " using original logic"
                )
                if filter_type == "all":
                    records = self.reconciliation_repository.get_paginated(
                        limit, offset
                    )
                    total_count = self.reconciliation_repository.get_count()
                else:
                    records = (
                        self.reconciliation_repository.get_filtered_paginated(
                            filter_type, limit, offset
                        )
                    )
                    total_count = (
                        self.reconciliation_repository
                        .get_filtered_count(filter_type)
                    )

            result_list = [record.serialize() for record in records]
            logger.info(f"Serialized {len(result_list)} records")

            return {
                "data": result_list,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "next_offset": (
                        offset + limit
                        if offset + limit < total_count else None
                    ),
                },
                "filters": {
                    "filter_type": filter_type,
                    "start_date": start_date,
                    "end_date": end_date,
                    "flight_number": flight_number,  # Add this
                },
            }
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Exception in get_paginated_reconciliation_data: {str(e)}")
            logger.error(f"Traceback: {error_details}")

            return {
                "message": "Failed to retrieve reconciliation data",
                "error": str(e),
            }, 501

    def get_reconciliation_summary(self, start_date=None, end_date=None):
        """
        Get summary statistics for the reconciliation data using SQLAlchemy
        """
        try:
            logger.info("=== get_reconciliation_summary called ===")
            records = self.reconciliation_repository.get_all()
            logger.info(f"Processing {len(records)} records for summary")

            total_records = len(records)
            matching_records = sum(
                1 for r in records if r.Air == "Yes" and r.Cat == "Yes"
            )
            air_only_records = sum(
                1 for r in records if r.Air == "Yes" and r.Cat == "No"
            )
            cat_only_records = sum(
                1 for r in records if r.Air == "No" and r.Cat == "Yes"
            )
            quantity_discrepancies = sum(
                1 for r in records if r.DifQty == "Yes"
            )
            price_discrepancies = sum(
                1 for r in records if r.DifPrice == "Yes"
            )
            total_discrepancies = sum(
                1 for r in records if r.DifQty == "Yes" or r.DifPrice == "Yes"
            )

            total_amount_difference = 0
            for record in records:
                if record.AmountDif and record.AmountDif.strip():
                    try:
                        total_amount_difference += float(record.AmountDif)
                    except (ValueError, TypeError):
                        pass

            logger.info(
                f"Summary calculated: total={total_records}, "
                f"matching={matching_records}"
            )

            return {
                "summary": {
                    "total_records": total_records,
                    "matching_records": matching_records,
                    "air_only_records": air_only_records,
                    "cat_only_records": cat_only_records,
                    "quantity_discrepancies": quantity_discrepancies,
                    "price_discrepancies": price_discrepancies,
                    "total_discrepancies": total_discrepancies,
                    "total_amount_difference": total_amount_difference,
                }
            }
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Exception in get_reconciliation_summary: {str(e)}")
            logger.error(f"Traceback: {error_details}")

            return {
                "message": "Failed to retrieve reconciliation summary",
                "error": str(e),
            }, 501
