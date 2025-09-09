# Repositories
from repositories.repository import Repository
from typing import List, Dict
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

import logging
import os

# Tables - only keeping essential ones
from models.schema_ccs import (
    CateringInvoiceReport,
    AirCompanyInvoiceReport,
    Reconciliation,
    FlightNumberMapping,
    FlightClassMapping,
    ReconAnnotation,
)

# Application-Specific Common Utilities
from common.custom_exception import CustomException

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger()


class CateringInvoiceRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, CateringInvoiceReport)

    def insert_billing_recon(
        self,
        facility=None,
        flt_date=None,
        flt_no=None,
        flt_inv=None,
        class_=None,
        item_group=None,
        itemcode=None,
        item_desc=None,
        al_bill_code=None,
        al_bill_desc=None,
        bill_catg=None,
        unit=None,
        pax=None,
        qty=None,
        unit_price=None,
        total_amount=None
    ):
        try:
            new_record = CateringInvoiceReport(
                facility=facility,
                flt_date=flt_date,
                flt_no=flt_no,
                flt_inv=flt_inv,
                class_=class_,
                item_group=item_group,
                itemcode=itemcode,
                item_desc=item_desc,
                al_bill_code=al_bill_code,
                al_bill_desc=al_bill_desc,
                bill_catg=bill_catg,
                unit=unit,
                pax=pax,
                qty=qty,
                unit_price=unit_price,
                total_amount=total_amount
            )
            
            self.session.add(new_record)
            self.session.commit()
            result = new_record
            logger.info(f"Billing recon record inserted successfully")
            return result
        except Exception as e:
            logger.error(f"Error inserting billing recon record: {str(e)}")
            raise CustomException(f"Failed to insert billing recon record: {str(e)}")

    def get_all_catering_data(self):
        """Get all catering invoice data"""
        try:
            return self.get_all()
        except Exception as e:
            logger.error(f"Error getting all catering data: {str(e)}")
            raise CustomException(f"Failed to get catering data: {str(e)}")

    def delete_all_catering_data(self):
        """Delete all catering invoice data"""
        try:
            self.session.query(CateringInvoiceReport).delete()
            self.session.commit()
            logger.info("All catering invoice data deleted successfully")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting all catering data: {str(e)}")
            raise CustomException(f"Failed to delete catering data: {str(e)}")


class AirCompanyInvoiceRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, AirCompanyInvoiceReport)

    def insert_air_company_invoice(
        self,
        supplier=None,
        flight_date=None,
        flight_no=None,
        dep=None,
        arr=None,
        class_=None,
        invoiced_pax=None,
        service_code=None,
        supplier_code=None,
        service_description=None,
        aircraft=None,
        qty=None,
        unit_price=None,
        sub_total=None,
        tax=None,
        total_inc_tax=None,
        currency=None,
        item_status=None,
        invoice_status=None,
        invoice_date=None,
        paid_date=None,
        flight_no_red=None
    ):
        try:
            new_record = AirCompanyInvoiceReport(
                supplier=supplier,
                flight_date=flight_date,
                flight_no=flight_no,
                dep=dep,
                arr=arr,
                class_=class_,
                invoiced_pax=invoiced_pax,
                service_code=service_code,
                supplier_code=supplier_code,
                service_description=service_description,
                aircraft=aircraft,
                qty=qty,
                unit_price=unit_price,
                sub_total=sub_total,
                tax=tax,
                total_inc_tax=total_inc_tax,
                currency=currency,
                item_status=item_status,
                invoice_status=invoice_status,
                invoice_date=invoice_date,
                paid_date=paid_date,
                flight_no_red=flight_no_red
            )
            
            self.session.add(new_record)
            self.session.commit()
            result = new_record
            logger.info(f"Air company invoice record inserted successfully")
            return result
        except Exception as e:
            logger.error(f"Error inserting air company invoice record: {str(e)}")
            raise CustomException(f"Failed to insert air company invoice record: {str(e)}")

    def get_all_air_company_data(self):
        """Get all air company invoice data"""
        try:
            return self.get_all()
        except Exception as e:
            logger.error(f"Error getting all air company data: {str(e)}")
            raise CustomException(f"Failed to get air company data: {str(e)}")

    def delete_all_air_company_data(self):
        """Delete all air company invoice data"""
        try:
            self.session.query(AirCompanyInvoiceReport).delete()
            self.session.commit()
            logger.info("All air company invoice data deleted successfully")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting all air company data: {str(e)}")
            raise CustomException(f"Failed to delete air company data: {str(e)}")


class ReconciliationRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        """Get all reconciliation records"""
        return (
            self.session.query(Reconciliation)
            .order_by(Reconciliation.AirFlightDate, Reconciliation.AirFlightNo)
            .all()
        )

    def get_paginated(self, limit=100, offset=0):
        """Get paginated reconciliation records"""
        return (
            self.session.query(Reconciliation)
            .order_by(Reconciliation.AirFlightDate, Reconciliation.AirFlightNo)
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_count(self):
        """Get total count of reconciliation records"""
        return self.session.query(Reconciliation).count()

    def get_by_date_range(self, start_date, end_date, limit=None, offset=None):
        """Get reconciliation records filtered by FLIGHT DATE range"""
        air_query = self.session.query(Reconciliation).filter(
            func.date(Reconciliation.AirFlightDate) >= start_date,
            func.date(Reconciliation.AirFlightDate) <= end_date,
        )

        cat_query = self.session.query(Reconciliation).filter(
            func.date(Reconciliation.CatFltDate) >= start_date,
            func.date(Reconciliation.CatFltDate) <= end_date,
        )

        combined_query = air_query.union(cat_query).order_by(
            Reconciliation.AirFlightDate, Reconciliation.AirFlightNo
        )

        if offset is not None:
            combined_query = combined_query.offset(offset)
        if limit is not None:
            combined_query = combined_query.limit(limit)

        return combined_query.all()

    def get_count_by_date_range(self, start_date, end_date):
        """Get count of records in flight date range"""
        air_query = self.session.query(Reconciliation).filter(
            func.date(Reconciliation.AirFlightDate) >= start_date,
            func.date(Reconciliation.AirFlightDate) <= end_date,
        )

        cat_query = self.session.query(Reconciliation).filter(
            func.date(Reconciliation.CatFltDate) >= start_date,
            func.date(Reconciliation.CatFltDate) <= end_date,
        )

        combined_query = air_query.union(cat_query)
        return combined_query.count()

    def get_by_flight_number(self, flight_number, limit=None, offset=None):
        """Get reconciliation records filtered by flight number"""
        query = (
            self.session.query(Reconciliation)
            .filter(
                (Reconciliation.AirFlightNo.ilike(f"%{flight_number}%"))
                | (Reconciliation.CatFltNo.ilike(f"%{flight_number}%"))
            )
            .order_by(Reconciliation.AirFlightDate, Reconciliation.AirFlightNo)
        )

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return query.all()

    def get_count_by_flight_number(self, flight_number):
        """Get count of records filtered by flight number"""
        return (
            self.session.query(Reconciliation)
            .filter(
                (Reconciliation.AirFlightNo.ilike(f"%{flight_number}%"))
                | (Reconciliation.CatFltNo.ilike(f"%{flight_number}%"))
            )
            .count()
        )


class FlightClassMappingRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        """Get all flight class mappings"""
        return self.session.query(FlightClassMapping).all()

    def get_by_promeus_class(self, promeus_class):
        """Get mapping by Promeus class"""
        return (
            self.session.query(FlightClassMapping)
            .filter(FlightClassMapping.PromeusClass == promeus_class)
            .first()
        )

    def get_by_inflair_class(self, inflair_class):
        """Get mapping by Inflair class"""
        return (
            self.session.query(FlightClassMapping)
            .filter(FlightClassMapping.InflairClass == inflair_class)
            .first()
        )

    def insert(self, mapping):
        """Insert a new flight class mapping"""
        try:
            self.session.add(mapping)
            self.session.commit()
            return mapping
        except Exception as e:
            self.session.rollback()
            raise e

    def update(self, mapping):
        """Update a flight class mapping"""
        try:
            self.session.commit()
            return mapping
        except Exception as e:
            self.session.rollback()
            raise e

    def delete(self, mapping_id):
        """Delete a flight class mapping"""
        try:
            mapping = self.session.query(FlightClassMapping).filter(
                FlightClassMapping.Id == mapping_id
            ).first()
            if mapping:
                self.session.delete(mapping)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise e


class FlightNumberMappingRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        """Get all flight number mappings"""
        return self.session.query(FlightNumberMapping).all()

    def get_by_air_company_flight_number(self, flight_number):
        """Get mapping by air company flight number"""
        return (
            self.session.query(FlightNumberMapping)
            .filter(FlightNumberMapping.AirCompanyFlightNumber == flight_number)
            .first()
        )

    def get_by_catering_flight_number(self, flight_number):
        """Get mapping by catering flight number"""
        return (
            self.session.query(FlightNumberMapping)
            .filter(FlightNumberMapping.CateringFlightNumber == flight_number)
            .first()
        )

    def insert(self, mapping):
        """Insert a new flight number mapping"""
        try:
            self.session.add(mapping)
            self.session.commit()
            return mapping
        except Exception as e:
            self.session.rollback()
            raise e

    def update(self, mapping):
        """Update a flight number mapping"""
        try:
            self.session.commit()
            return mapping
        except Exception as e:
            self.session.rollback()
            raise e

    def delete(self, mapping_id):
        """Delete a flight number mapping"""
        try:
            mapping = self.session.query(FlightNumberMapping).filter(
                FlightNumberMapping.Id == mapping_id
            ).first()
            if mapping:
                self.session.delete(mapping)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise e
