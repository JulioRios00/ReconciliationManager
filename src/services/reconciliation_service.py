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
        """
        Retrieve all data from the
        ccs.Reconciliation table using SQLAlchemy
        """
        try:
            records = self.reconciliation_repository.get_all()
            result_list = [record.serialize() for record in records]
            return {"data": result_list}
        except Exception as e:
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
        flight_number=None,
        item_name=None,
    ):
        """Retrieve paginated data from the
        ccs.Reconciliation table using SQLAlchemy
        """
        try:
            parsed_start_date = (
                self._parse_date(start_date) if start_date else None
            )
            parsed_end_date = self._parse_date(end_date) if end_date else None

            if (
                parsed_start_date
                and parsed_end_date
                and flight_number
                and item_name
            ):
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
                            filter_type, parsed_start_date, parsed_end_date
                        )
                    )
            elif parsed_start_date and parsed_end_date and item_name:
                if filter_type == "all":
                    records = (
                        self.reconciliation_repository
                        .get_by_item_name_and_date_range(
                            item_name,
                            parsed_start_date,
                            parsed_end_date,
                            limit,
                            offset
                        )
                    )
                    total_count = (
                        self.reconciliation_repository
                        .get_count_by_item_name_and_date_range(
                            item_name, parsed_start_date, parsed_end_date
                        )
                    )
                else:
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
                            filter_type, parsed_start_date, parsed_end_date
                        )
                    )
            elif flight_number and item_name:
                if filter_type == "all":
                    records = (
                        self.reconciliation_repository
                        .get_by_item_name_and_flight_number(
                            item_name, flight_number, limit, offset
                        )
                    )
                    total_count = (
                        self.reconciliation_repository
                        .get_count_by_item_name_and_flight_number(
                            item_name, flight_number
                        )
                    )
                else:
                    records = (
                        self.reconciliation_repository.
                        get_filtered_by_flight_number(
                            filter_type, flight_number, limit, offset
                        )
                    )
                    total_count = (
                        self.reconciliation_repository
                        .get_filtered_count_by_flight_number(
                            filter_type, flight_number
                        )
                    )
            elif parsed_start_date and parsed_end_date:
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
                            filter_type, parsed_start_date, parsed_end_date
                        )
                    )
            elif flight_number:
                if filter_type == "all":
                    records = (
                        self.reconciliation_repository
                        .get_by_flight_number(
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
                    records = (
                        self.reconciliation_repository
                        .get_filtered_by_flight_number(
                            filter_type, flight_number, limit, offset
                        )
                    )
                    total_count = (
                        self.reconciliation_repository
                        .get_filtered_count_by_flight_number(
                            filter_type, flight_number
                        )
                    )
            elif item_name:
                if filter_type == "all":
                    records = (
                        self.reconciliation_repository.get_by_item_name(
                            item_name, limit, offset
                        )
                    )
                    total_count = (
                        self.reconciliation_repository.get_count_by_item_name(
                            item_name
                        )
                    )
                else:
                    records = (
                        self.reconciliation_repository.
                        get_filtered_by_item_name(
                            filter_type, item_name, limit, offset
                        )
                    )
                    total_count = (
                        self.reconciliation_repository
                        .get_filtered_count_by_item_name(
                            filter_type, item_name
                        )
                    )
            else:
                if filter_type == "all":
                    records = self.reconciliation_repository.get_paginated(
                        limit, offset
                    )
                    total_count = self.reconciliation_repository.get_count()
                else:
                    records = (
                        self.reconciliation_repository
                        .get_filtered_paginated(
                            filter_type, limit, offset
                        )
                    )
                    total_count = (
                        self.reconciliation_repository.get_filtered_count(
                            filter_type
                        )
                    )

            result_list = [record.serialize() for record in records]

            return {
                "data": result_list,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "next_offset": (
                        offset + limit
                        if offset + limit < total_count
                        else None
                    ),
                },
                "filters": {
                    "filter_type": filter_type,
                    "start_date": start_date,
                    "end_date": end_date,
                    "flight_number": flight_number,
                    "item_name": item_name,
                },
            }
        except Exception as e:
            return {
                "message": "Failed to retrieve reconciliation data",
                "error": str(e),
            }, 501

    def get_reconciliation_summary(self):
        """
        Get summary statistics for the reconciliation data using SQLAlchemy
        """
        try:
            records = self.reconciliation_repository.get_all()

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
            return {
                "message": "Failed to retrieve reconciliation summary",
                "error": str(e),
            }, 501

    def get_invoice_reports_data(
        self,
        limit=100,
        offset=0,
        start_date=None,
        end_date=None,
        flight_number=None,
        report_type="both",
    ):
        """
        Retrieve data from AirCompanyInvoiceReport and/or
        CateringInvoiceReport tables

        Args:
            limit: Number of records per page
            offset: Number of records to skip
            start_date: Filter by start date (YYYY-MM-DD format)
            end_date: Filter by end date (YYYY-MM-DD format)
            flight_number: Filter by flight number
            report_type: 'air', 'catering', or 'both' (default)
        """
        try:
            parsed_start_date = (
                self._parse_date(start_date) if start_date else None
            )
            parsed_end_date = self._parse_date(end_date) if end_date else None

            result = {}

            if report_type in ["air", "both"]:
                air_records = (
                    self.reconciliation_repository
                    .get_air_company_invoice_reports(
                        limit=limit,
                        offset=offset,
                        start_date=parsed_start_date,
                        end_date=parsed_end_date,
                        flight_number=flight_number,
                    )
                )
                air_count = (
                    self.reconciliation_repository
                    .get_air_company_invoice_reports_count(
                        start_date=parsed_start_date,
                        end_date=parsed_end_date,
                        flight_number=flight_number,
                    )
                )
                result["air_company_reports"] = {
                    "data": [record.serialize() for record in air_records],
                    "total_count": air_count,
                }

            if report_type in ["catering", "both"]:
                catering_records = (
                    self.reconciliation_repository
                    .get_catering_invoice_reports(
                        limit=limit,
                        offset=offset,
                        start_date=parsed_start_date,
                        end_date=parsed_end_date,
                        flight_number=flight_number,
                    )
                )
                catering_count = (
                    self.reconciliation_repository
                    .get_catering_invoice_reports_count(
                        start_date=parsed_start_date,
                        end_date=parsed_end_date,
                        flight_number=flight_number,
                    )
                )
                result["catering_reports"] = {
                    "data": (
                        [record.serialize() for record in catering_records]
                    ),
                    "total_count": catering_count,
                }

            result["pagination"] = {
                "limit": limit,
                "offset": offset,
                "next_offset": None,
            }

            result["filters"] = {
                "start_date": start_date,
                "end_date": end_date,
                "flight_number": flight_number,
                "report_type": report_type,
            }

            if report_type == "air" and "air_company_reports" in result:
                total_count = result["air_company_reports"]["total_count"]
                result["pagination"]["next_offset"] = (
                    offset + limit if offset + limit < total_count else None
                )
            elif report_type == "catering" and "catering_reports" in result:
                total_count = result["catering_reports"]["total_count"]
                result["pagination"]["next_offset"] = (
                    offset + limit if offset + limit < total_count else None
                )
            elif report_type == "both":
                max_count = 0
                if "air_company_reports" in result:
                    max_count = max(
                        max_count, result["air_company_reports"]["total_count"]
                    )
                if "catering_reports" in result:
                    max_count = max(
                        max_count, result["catering_reports"]["total_count"]
                    )
                result["pagination"]["next_offset"] = (
                    offset + limit if offset + limit < max_count else None
                )

            return result

        except Exception as e:
            return {
                "message": "Failed to retrieve invoice reports data",
                "error": str(e),
            }, 501

    def get_all_air_company_reports(self, limit=None, offset=None):
        """
        Retrieve all data from the AirCompanyInvoiceReport
        with optional pagination
        """
        try:
            if limit is not None and offset is not None:
                records = (
                    self.reconciliation_repository
                    .get_air_company_invoice_reports(
                        limit=limit, offset=offset
                    )
                )
                total_count = (
                    self.reconciliation_repository
                    .get_air_company_invoice_reports_count()
                )
                result_list = [record.serialize() for record in records]
                return {
                    "data": result_list,
                    "pagination": {
                        "limit": limit,
                        "offset": offset,
                        "total": total_count,
                        "has_more": offset + limit < total_count,
                    },
                }
            else:
                records = (
                    self.reconciliation_repository
                    .get_all_air_company_reports()
                )
                result_list = [record.serialize() for record in records]
                return {"data": result_list}
        except Exception as e:
            return {
                "message": "Failed to retrieve air company invoice reports",
                "error": str(e),
            }, 501

    def get_all_catering_reports(self, limit=None, offset=None):
        """
        Retrieve all data from the CateringInvoiceReport 
        table using SQLAlchemy with optional pagination
        """
        try:
            if limit is not None and offset is not None:
                records = (
                    self.reconciliation_repository
                    .get_catering_invoice_reports(
                        limit=limit, offset=offset
                    )
                )
                total_count = (
                    self.reconciliation_repository
                    .get_catering_invoice_reports_count()
                )

                result_list = [record.serialize() for record in records]
                return {
                    "data": result_list,
                    "pagination": {
                        "limit": limit,
                        "offset": offset,
                        "total": total_count,
                        "has_more": offset + limit < total_count,
                    },
                }
            else:
                records = (
                    self.reconciliation_repository.get_all_catering_reports()
                )
                result_list = [record.serialize() for record in records]
                return {"data": result_list}
        except Exception as e:
            return {
                "message": "Failed to retrieve catering invoice reports",
                "error": str(e),
            }, 501
