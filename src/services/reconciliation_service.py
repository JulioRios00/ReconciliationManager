import uuid
from datetime import datetime

from src.models.schema_ccs import (
    AirCompanyInvoiceReport,
    CateringInvoiceReport,
    Reconciliation,
)
from src.repositories.reconciliation_repository import ReconciliationRepository


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
            parsed_start_date = self._parse_date(start_date) if start_date else None
            parsed_end_date = self._parse_date(end_date) if end_date else None

            if parsed_start_date and parsed_end_date and flight_number and item_name:
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
                    records = self.reconciliation_repository.get_filtered_by_date_range(
                        filter_type, parsed_start_date, parsed_end_date, limit, offset
                    )
                    total_count = (
                        self.reconciliation_repository.get_filtered_count_by_date_range(
                            filter_type, parsed_start_date, parsed_end_date
                        )
                    )
            elif parsed_start_date and parsed_end_date and item_name:
                if filter_type == "all":
                    records = (
                        self.reconciliation_repository.get_by_item_name_and_date_range(
                            item_name, parsed_start_date, parsed_end_date, limit, offset
                        )
                    )
                    total_count = self.reconciliation_repository.get_count_by_item_name_and_date_range(
                        item_name, parsed_start_date, parsed_end_date
                    )
                else:
                    records = self.reconciliation_repository.get_filtered_by_date_range(
                        filter_type, parsed_start_date, parsed_end_date, limit, offset
                    )
                    total_count = (
                        self.reconciliation_repository.get_filtered_count_by_date_range(
                            filter_type, parsed_start_date, parsed_end_date
                        )
                    )
            elif flight_number and item_name:
                if filter_type == "all":
                    records = self.reconciliation_repository.get_by_item_name_and_flight_number(
                        item_name, flight_number, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_count_by_item_name_and_flight_number(
                        item_name, flight_number
                    )
                else:
                    records = (
                        self.reconciliation_repository.get_filtered_by_flight_number(
                            filter_type, flight_number, limit, offset
                        )
                    )
                    total_count = self.reconciliation_repository.get_filtered_count_by_flight_number(
                        filter_type, flight_number
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
                    records = self.reconciliation_repository.get_filtered_by_date_range(
                        filter_type, parsed_start_date, parsed_end_date, limit, offset
                    )
                    total_count = (
                        self.reconciliation_repository.get_filtered_count_by_date_range(
                            filter_type, parsed_start_date, parsed_end_date
                        )
                    )
            elif flight_number:
                if filter_type == "all":
                    records = self.reconciliation_repository.get_by_flight_number(
                        flight_number, limit, offset
                    )
                    total_count = (
                        self.reconciliation_repository.get_count_by_flight_number(
                            flight_number
                        )
                    )
                else:
                    records = (
                        self.reconciliation_repository.get_filtered_by_flight_number(
                            filter_type, flight_number, limit, offset
                        )
                    )
                    total_count = self.reconciliation_repository.get_filtered_count_by_flight_number(
                        filter_type, flight_number
                    )
            elif item_name:
                if filter_type == "all":
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
                    total_count = (
                        self.reconciliation_repository.get_filtered_count_by_item_name(
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
                    records = self.reconciliation_repository.get_filtered_paginated(
                        filter_type, limit, offset
                    )
                    total_count = self.reconciliation_repository.get_filtered_count(
                        filter_type
                    )

            result_list = [record.serialize() for record in records]

            return {
                "data": result_list,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "next_offset": (
                        offset + limit if offset + limit < total_count else None
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
            quantity_discrepancies = sum(1 for r in records if r.DifQty == "Yes")
            price_discrepancies = sum(1 for r in records if r.DifPrice == "Yes")
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
            parsed_start_date = self._parse_date(start_date) if start_date else None
            parsed_end_date = self._parse_date(end_date) if end_date else None

            result = {}

            if report_type in ["air", "both"]:
                air_records = (
                    self.reconciliation_repository.get_air_company_invoice_reports(
                        limit=limit,
                        offset=offset,
                        start_date=parsed_start_date,
                        end_date=parsed_end_date,
                        flight_number=flight_number,
                    )
                )
                air_count = self.reconciliation_repository.get_air_company_invoice_reports_count(
                    start_date=parsed_start_date,
                    end_date=parsed_end_date,
                    flight_number=flight_number,
                )
                result["air_company_reports"] = {
                    "data": [record.serialize() for record in air_records],
                    "total_count": air_count,
                }

            if report_type in ["catering", "both"]:
                catering_records = (
                    self.reconciliation_repository.get_catering_invoice_reports(
                        limit=limit,
                        offset=offset,
                        start_date=parsed_start_date,
                        end_date=parsed_end_date,
                        flight_number=flight_number,
                    )
                )
                catering_count = (
                    self.reconciliation_repository.get_catering_invoice_reports_count(
                        start_date=parsed_start_date,
                        end_date=parsed_end_date,
                        flight_number=flight_number,
                    )
                )
                result["catering_reports"] = {
                    "data": ([record.serialize() for record in catering_records]),
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
                    self.reconciliation_repository.get_air_company_invoice_reports(
                        limit=limit, offset=offset
                    )
                )
                total_count = (
                    self.reconciliation_repository.get_air_company_invoice_reports_count()
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
                records = self.reconciliation_repository.get_all_air_company_reports()
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
                records = self.reconciliation_repository.get_catering_invoice_reports(
                    limit=limit, offset=offset
                )
                total_count = (
                    self.reconciliation_repository.get_catering_invoice_reports_count()
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
                records = self.reconciliation_repository.get_all_catering_reports()
                result_list = [record.serialize() for record in records]
                return {"data": result_list}
        except Exception as e:
            return {
                "message": "Failed to retrieve catering invoice reports",
                "error": str(e),
            }, 501

    def populate_reconciliation_table(self):
        """
        Populate the Reconciliation table with data from AirCompanyInvoiceReport
        and CateringInvoiceReport tables using SQLAlchemy ORM.
        """
        try:

            deleted = self.session.query(Reconciliation).delete()
            self.session.flush()

            air_records = (
                self.session.query(AirCompanyInvoiceReport)
                .filter(
                    AirCompanyInvoiceReport.Ativo.is_(True),
                    AirCompanyInvoiceReport.Excluido.is_(False),
                )
                .all()
            )

            catering_records = (
                self.session.query(CateringInvoiceReport)
                .filter(
                    CateringInvoiceReport.Ativo.is_(True),
                    CateringInvoiceReport.Excluido.is_(False),
                )
                .all()
            )

            if not air_records:
                air_records = self.session.query(AirCompanyInvoiceReport).all()

            if not catering_records:
                catering_records = self.session.query(CateringInvoiceReport).all()

            catering_by_date = {}
            catering_by_date_class = {}
            catering_by_date_facility = {}

            for cat in catering_records:
                date_key = cat.FltDate
                class_key = (cat.FltDate, (cat.Class or "").strip().upper())
                facility_key = (cat.FltDate, cat.Facility)

                if date_key:
                    catering_by_date.setdefault(date_key, []).append(cat)
                if cat.Class and date_key:
                    catering_by_date_class.setdefault(class_key, []).append(cat)
                if cat.Facility and date_key:
                    catering_by_date_facility.setdefault(facility_key, []).append(cat)

            processed_catering_ids = set()
            reconciliation_records = []
            matched_count = 0
            air_only_count = 0

            for i, air in enumerate(air_records):
                matched = False
                date_class_key = (air.FlightDate, (air.Class or "").strip().upper())
                available = catering_by_date_class.get(date_class_key, [])

                for cat in available:
                    if cat.Id not in processed_catering_ids:
                        reconciliation_records.append(
                            self._create_matched_reconciliation_record(air, cat)
                        )
                        processed_catering_ids.add(cat.Id)
                        matched = True
                        matched_count += 1
                        break

                if not matched and air.FlightDate:
                    for cat in catering_by_date.get(air.FlightDate, []):
                        if cat.Id not in processed_catering_ids:
                            reconciliation_records.append(
                                self._create_matched_reconciliation_record(air, cat)
                            )
                            processed_catering_ids.add(cat.Id)
                            matched = True
                            matched_count += 1
                            break

                if not matched:
                    reconciliation_records.append(
                        self._create_air_only_reconciliation_record(air)
                    )
                    air_only_count += 1

            catering_only_count = 0
            for cat in catering_records:
                if cat.Id not in processed_catering_ids:
                    reconciliation_records.append(
                        self._create_catering_only_reconciliation_record(cat)
                    )
                    catering_only_count += 1

            if reconciliation_records:
                self.session.bulk_save_objects(reconciliation_records)
                self.session.flush()

            self._calculate_reconciliation_differences()

            self.session.commit()

            return {
                "success": True,
                "message": "Reconciliation table populated successfully",
                "summary": {
                    "total_records": len(reconciliation_records),
                    "matched_records": matched_count,
                    "catering_only_records": catering_only_count,
                    "air_only_records": air_only_count,
                },
            }

        except Exception as e:
            self.session.rollback()
            print(f"❌ ERROR: {str(e)}")
            import traceback

            traceback.print_exc()
            return {
                "success": False,
                "message": f"Error populating reconciliation table: {str(e)}",
            }

    def _calculate_reconciliation_differences(self):
        """Calculate differences and update flags for matched records"""
        try:
            matched_records = (
                self.session.query(Reconciliation)
                .filter(Reconciliation.Air == "Yes", Reconciliation.Cat == "Yes")
                .all()
            )

            for record in matched_records:
                record.DifQty = "No"
                record.DifPrice = "No"
                record.AmountDif = "0.00"
                record.QtyDif = "0"

                air_qty = self._safe_int(record.AirQty, 0)
                cat_qty = self._safe_int(record.CatQty, 0)
                air_subtotal = self._safe_float(record.AirSubTotal, 0.0)
                cat_total = self._safe_float(record.CatTotalAmount, 0.0)

                if air_qty != cat_qty:
                    record.DifQty = "Yes"
                    record.QtyDif = str(cat_qty - air_qty)

                if abs(air_subtotal - cat_total) > 0.01:
                    record.DifPrice = "Yes"
                    record.AmountDif = str(round(cat_total - air_subtotal, 2))

            self.session.flush()

        except Exception as e:
            raise Exception(f"Error calculating differences: {str(e)}")

    def _safe_int(self, value, default=0):
        """Safely convert string to int with default"""
        if not value or value == "None" or value is None:
            return default
        try:
            return int(float(str(value)))
        except (ValueError, TypeError):
            return default

    def _safe_float(self, value, default=0.0):
        """Safely convert string to float with default"""
        if not value or value == "None" or value is None:
            return default
        try:
            if isinstance(value, str):
                value = value.replace(",", ".")
            return float(value)
        except (ValueError, TypeError):
            return default

    def _create_matched_reconciliation_record(self, air_record, cat_record):
        """Create a reconciliation record for matched air and catering records"""
        return Reconciliation(
            Id=uuid.uuid4(),
            DataCriacao=datetime.now(),
            Ativo=True,
            Excluido=False,
            # Air Company data
            AirSupplier=air_record.Supplier,
            AirFlightDate=air_record.FlightDate,
            AirFlightNo=air_record.FlightNo,
            AirDep=air_record.Dep,
            AirArr=air_record.Arr,
            AirClass=air_record.Class,
            AirInvoicedPax=air_record.InvoicedPax,
            AirServiceCode=air_record.ServiceCode,
            AirSupplierCode=air_record.SupplierCode,
            AirServiceDescription=air_record.ServiceDescription,
            AirAircraft=air_record.Aircraft,
            AirQty=str(air_record.Qty) if air_record.Qty is not None else "0",
            AirUnitPrice=(
                str(air_record.UnitPrice) if air_record.UnitPrice is not None else "0"
            ),
            AirSubTotal=(
                str(air_record.SubTotal) if air_record.SubTotal is not None else "0.00"
            ),
            AirTax=str(air_record.Tax) if air_record.Tax is not None else "0.00",
            AirTotalIncTax=(
                str(air_record.TotalIncTax)
                if air_record.TotalIncTax is not None
                else "0.00"
            ),
            AirCurrency=air_record.Currency,
            AirItemStatus=air_record.ItemStatus,
            AirInvoiceStatus=air_record.InvoiceStatus,
            AirInvoiceDate=air_record.InvoiceDate,
            AirPaidDate=air_record.PaidDate,
            AirFlightNoRed=air_record.FlightNoRed,
            # Catering data
            CatFacility=cat_record.Facility,
            CatFltDate=cat_record.FltDate,
            CatFltNo=cat_record.FltNo,
            CatFltInv=cat_record.FltInv,
            CatClass=cat_record.Class,
            CatItemGroup=cat_record.ItemGroup,
            CatItemcode=cat_record.Itemcode,
            CatItemDesc=cat_record.ItemDesc,
            CatAlBillCode=cat_record.AlBillCode,
            CatAlBillDesc=cat_record.AlBillDesc,
            CatBillCatg=cat_record.BillCatg,
            CatUnit=cat_record.Unit,
            CatPax=cat_record.Pax,
            CatQty=cat_record.Qty,
            CatUnitPrice=cat_record.UnitPrice,
            CatTotalAmount=cat_record.TotalAmount,
            # Flags
            Air="Yes",
            Cat="Yes",
        )

    def _create_air_only_reconciliation_record(self, air_record):
        """Create a reconciliation record for air-only records"""
        return Reconciliation(
            Id=uuid.uuid4(),
            DataCriacao=datetime.now(),
            Ativo=True,
            Excluido=False,
            # Air Company data
            AirSupplier=air_record.Supplier,
            AirFlightDate=air_record.FlightDate,
            AirFlightNo=air_record.FlightNo,
            AirDep=air_record.Dep,
            AirArr=air_record.Arr,
            AirClass=air_record.Class,
            AirInvoicedPax=air_record.InvoicedPax,
            AirServiceCode=air_record.ServiceCode,
            AirSupplierCode=air_record.SupplierCode,
            AirServiceDescription=air_record.ServiceDescription,
            AirAircraft=air_record.Aircraft,
            AirQty=str(air_record.Qty) if air_record.Qty is not None else "0",
            AirUnitPrice=(
                str(air_record.UnitPrice) if air_record.UnitPrice is not None else "0"
            ),
            AirSubTotal=(
                str(air_record.SubTotal) if air_record.SubTotal is not None else "0.00"
            ),
            AirTax=str(air_record.Tax) if air_record.Tax is not None else "0.00",
            AirTotalIncTax=(
                str(air_record.TotalIncTax)
                if air_record.TotalIncTax is not None
                else "0.00"
            ),
            AirCurrency=air_record.Currency,
            AirItemStatus=air_record.ItemStatus,
            AirInvoiceStatus=air_record.InvoiceStatus,
            AirInvoiceDate=air_record.InvoiceDate,
            AirPaidDate=air_record.PaidDate,
            AirFlightNoRed=air_record.FlightNoRed,
            # Flags
            Air="Yes",
            Cat="No",
        )

    def _create_catering_only_reconciliation_record(self, cat_record):
        """Create a reconciliation record for catering-only records"""
        return Reconciliation(
            Id=uuid.uuid4(),
            DataCriacao=datetime.now(),
            Ativo=True,
            Excluido=False,
            # Catering data
            CatFacility=cat_record.Facility,
            CatFltDate=cat_record.FltDate,
            CatFltNo=cat_record.FltNo,
            CatFltInv=cat_record.FltInv,
            CatClass=cat_record.Class,
            CatItemGroup=cat_record.ItemGroup,
            CatItemcode=cat_record.Itemcode,
            CatItemDesc=cat_record.ItemDesc,
            CatAlBillCode=cat_record.AlBillCode,
            CatAlBillDesc=cat_record.AlBillDesc,
            CatBillCatg=cat_record.BillCatg,
            CatUnit=cat_record.Unit,
            CatPax=cat_record.Pax,
            CatQty=cat_record.Qty,
            CatUnitPrice=cat_record.UnitPrice,
            CatTotalAmount=cat_record.TotalAmount,
            # Flags
            Air="No",
            Cat="Yes",
        )
