# Simplified repository for testing
from sqlalchemy.orm import Session

from models.schema_ccs import (
    AirCompanyInvoiceReport,
    CateringInvoiceReport,
    Reconciliation,
)


class ReconciliationRepository:
    """Simplified repository for testing ReconciliationService"""

    def __init__(self, db_session):
        self.session = db_session

    def get_all(self):
        """Get all reconciliation records"""
        return self.session.query(Reconciliation).all()

    def get_paginated(self, limit, offset):
        """Get paginated reconciliation records"""
        return self.session.query(Reconciliation).offset(offset).limit(limit).all()

    def get_count(self):
        """Get total count of reconciliation records"""
        return self.session.query(Reconciliation).count()

    def get_by_item_name(self, item_name, limit, offset):
        """Get records by item name"""
        return (
            self.session.query(Reconciliation)
            .filter(Reconciliation.CatItemDesc.contains(item_name))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_count_by_item_name(self, item_name):
        """Get count by item name"""
        return (
            self.session.query(Reconciliation)
            .filter(Reconciliation.CatItemDesc.contains(item_name))
            .count()
        )

    def get_by_date_range(self, start_date, end_date, limit, offset):
        """Get records by date range"""
        return (
            self.session.query(Reconciliation)
            .filter(Reconciliation.AirFlightDate.between(start_date, end_date))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_count_by_date_range(self, start_date, end_date):
        """Get count by date range"""
        return (
            self.session.query(Reconciliation)
            .filter(Reconciliation.AirFlightDate.between(start_date, end_date))
            .count()
        )

    def get_filtered_by_date_range(
        self, filter_type, start_date, end_date, limit, offset
    ):
        """Get filtered records by date range"""
        query = self.session.query(Reconciliation).filter(
            Reconciliation.AirFlightDate.between(start_date, end_date)
        )

        if filter_type == "matched":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "Yes"
            )
        elif filter_type == "air_only":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "No"
            )
        elif filter_type == "cat_only":
            query = query.filter(
                Reconciliation.Air == "No", Reconciliation.Cat == "Yes"
            )

        return query.offset(offset).limit(limit).all()

    def get_filtered_count_by_date_range(self, filter_type, start_date, end_date):
        """Get filtered count by date range"""
        query = self.session.query(Reconciliation).filter(
            Reconciliation.AirFlightDate.between(start_date, end_date)
        )

        if filter_type == "matched":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "Yes"
            )
        elif filter_type == "air_only":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "No"
            )
        elif filter_type == "cat_only":
            query = query.filter(
                Reconciliation.Air == "No", Reconciliation.Cat == "Yes"
            )

        return query.count()

    def get_by_item_name_and_date_range(
        self, item_name, start_date, end_date, limit, offset
    ):
        """Get records by item name and date range"""
        return (
            self.session.query(Reconciliation)
            .filter(
                Reconciliation.CatItemDesc.contains(item_name),
                Reconciliation.AirFlightDate.between(start_date, end_date),
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_count_by_item_name_and_date_range(self, item_name, start_date, end_date):
        """Get count by item name and date range"""
        return (
            self.session.query(Reconciliation)
            .filter(
                Reconciliation.CatItemDesc.contains(item_name),
                Reconciliation.AirFlightDate.between(start_date, end_date),
            )
            .count()
        )

    def get_by_flight_number(self, flight_number, limit, offset):
        """Get records by flight number"""
        return (
            self.session.query(Reconciliation)
            .filter(Reconciliation.AirFlightNo == flight_number)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_count_by_flight_number(self, flight_number):
        """Get count by flight number"""
        return (
            self.session.query(Reconciliation)
            .filter(Reconciliation.AirFlightNo == flight_number)
            .count()
        )

    def get_filtered_by_flight_number(self, filter_type, flight_number, limit, offset):
        """Get filtered records by flight number"""
        query = self.session.query(Reconciliation).filter(
            Reconciliation.AirFlightNo == flight_number
        )

        if filter_type == "matched":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "Yes"
            )
        elif filter_type == "air_only":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "No"
            )
        elif filter_type == "cat_only":
            query = query.filter(
                Reconciliation.Air == "No", Reconciliation.Cat == "Yes"
            )

        return query.offset(offset).limit(limit).all()

    def get_filtered_count_by_flight_number(self, filter_type, flight_number):
        """Get filtered count by flight number"""
        query = self.session.query(Reconciliation).filter(
            Reconciliation.AirFlightNo == flight_number
        )

        if filter_type == "matched":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "Yes"
            )
        elif filter_type == "air_only":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "No"
            )
        elif filter_type == "cat_only":
            query = query.filter(
                Reconciliation.Air == "No", Reconciliation.Cat == "Yes"
            )

        return query.count()

    def get_by_item_name_and_flight_number(
        self, item_name, flight_number, limit, offset
    ):
        """Get records by item name and flight number"""
        return (
            self.session.query(Reconciliation)
            .filter(
                Reconciliation.CatItemDesc.contains(item_name),
                Reconciliation.AirFlightNo == flight_number,
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_count_by_item_name_and_flight_number(self, item_name, flight_number):
        """Get count by item name and flight number"""
        return (
            self.session.query(Reconciliation)
            .filter(
                Reconciliation.CatItemDesc.contains(item_name),
                Reconciliation.AirFlightNo == flight_number,
            )
            .count()
        )

    def get_filtered_paginated(self, filter_type, limit, offset):
        """Get filtered paginated records"""
        query = self.session.query(Reconciliation)

        if filter_type == "matched":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "Yes"
            )
        elif filter_type == "air_only":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "No"
            )
        elif filter_type == "cat_only":
            query = query.filter(
                Reconciliation.Air == "No", Reconciliation.Cat == "Yes"
            )

        return query.offset(offset).limit(limit).all()

    def get_filtered_count(self, filter_type):
        """Get filtered count"""
        query = self.session.query(Reconciliation)

        if filter_type == "matched":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "Yes"
            )
        elif filter_type == "air_only":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "No"
            )
        elif filter_type == "cat_only":
            query = query.filter(
                Reconciliation.Air == "No", Reconciliation.Cat == "Yes"
            )

        return query.count()

    # Invoice report methods
    def get_air_company_invoice_reports(
        self,
        limit=None,
        offset=None,
        start_date=None,
        end_date=None,
        flight_number=None,
    ):
        """Get air company invoice reports"""
        query = self.session.query(AirCompanyInvoiceReport)

        if start_date and end_date:
            query = query.filter(
                AirCompanyInvoiceReport.FlightDate.between(start_date, end_date)
            )
        if flight_number:
            query = query.filter(AirCompanyInvoiceReport.FlightNo == flight_number)

        if limit is not None and offset is not None:
            query = query.offset(offset).limit(limit)

        return query.all()

    def get_air_company_invoice_reports_count(
        self, start_date=None, end_date=None, flight_number=None
    ):
        """Get air company invoice reports count"""
        query = self.session.query(AirCompanyInvoiceReport)

        if start_date and end_date:
            query = query.filter(
                AirCompanyInvoiceReport.FlightDate.between(start_date, end_date)
            )
        if flight_number:
            query = query.filter(AirCompanyInvoiceReport.FlightNo == flight_number)

        return query.count()

    def get_catering_invoice_reports(
        self,
        limit=None,
        offset=None,
        start_date=None,
        end_date=None,
        flight_number=None,
    ):
        """Get catering invoice reports"""
        query = self.session.query(CateringInvoiceReport)

        if start_date and end_date:
            query = query.filter(
                CateringInvoiceReport.FltDate.between(start_date, end_date)
            )
        if flight_number:
            query = query.filter(CateringInvoiceReport.FltNo == flight_number)

        if limit is not None and offset is not None:
            query = query.offset(offset).limit(limit)

        return query.all()

    def get_catering_invoice_reports_count(
        self, start_date=None, end_date=None, flight_number=None
    ):
        """Get catering invoice reports count"""
        query = self.session.query(CateringInvoiceReport)

        if start_date and end_date:
            query = query.filter(
                CateringInvoiceReport.FltDate.between(start_date, end_date)
            )
        if flight_number:
            query = query.filter(CateringInvoiceReport.FltNo == flight_number)

        return query.count()

    def get_all_air_company_reports(self):
        """Get all air company reports"""
        return self.session.query(AirCompanyInvoiceReport).all()

    def get_all_catering_reports(self):
        """Get all catering reports"""
        return self.session.query(CateringInvoiceReport).all()

    def get_filtered_by_item_name(self, filter_type, item_name, limit, offset):
        """Get filtered records by item name"""
        query = self.session.query(Reconciliation).filter(
            Reconciliation.CatItemDesc.contains(item_name)
        )

        if filter_type == "matched":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "Yes"
            )
        elif filter_type == "air_only":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "No"
            )
        elif filter_type == "cat_only":
            query = query.filter(
                Reconciliation.Air == "No", Reconciliation.Cat == "Yes"
            )

        return query.offset(offset).limit(limit).all()

    def get_filtered_count_by_item_name(self, filter_type, item_name):
        """Get filtered count by item name"""
        query = self.session.query(Reconciliation).filter(
            Reconciliation.CatItemDesc.contains(item_name)
        )

        if filter_type == "matched":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "Yes"
            )
        elif filter_type == "air_only":
            query = query.filter(
                Reconciliation.Air == "Yes", Reconciliation.Cat == "No"
            )
        elif filter_type == "cat_only":
            query = query.filter(
                Reconciliation.Air == "No", Reconciliation.Cat == "Yes"
            )

        return query.count()
