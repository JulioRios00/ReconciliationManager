from datetime import datetime
from repositories.ccs_repository import ReconciliationRepository
from models.schema_ccs import (
    AirCompanyInvoiceReport,
    CateringInvoiceReport,
    Reconciliation,
)
import uuid


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

            if (parsed_start_date and parsed_end_date and
                    flight_number and item_name):
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
                            filter_type,
                            parsed_start_date,
                            parsed_end_date
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
                            item_name,
                            parsed_start_date,
                            parsed_end_date
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
            print("=== Starting Reconciliation Table Population ===")
        
            # Clear existing reconciliation data
            deleted_count = self.session.query(Reconciliation).count()
            self.session.query(Reconciliation).delete()
            print(f"Cleared {deleted_count} existing reconciliation records")
        
            # Get all active records from both tables
            print("\n=== Fetching Records ===")
        
            # Check total counts first
            total_air_count = self.session.query(AirCompanyInvoiceReport).count()
            total_catering_count = self.session.query(CateringInvoiceReport).count()
            print(f"Total Air records in database: {total_air_count}")
            print(f"Total Catering records in database: {total_catering_count}")
        
            # Get active records
            air_records = self.session.query(AirCompanyInvoiceReport).filter(
                AirCompanyInvoiceReport.Ativo == True,
                AirCompanyInvoiceReport.Excluido == False
            ).all()
        
            catering_records = self.session.query(CateringInvoiceReport).filter(
                CateringInvoiceReport.Ativo == True,
                CateringInvoiceReport.Excluido == False
            ).all()
        
            print(f"Active Air records: {len(air_records)}")
            print(f"Active Catering records: {len(catering_records)}")
        
            # Check if we have no air records
            if len(air_records) == 0:
                print("❌ WARNING: No active air company records found!")
                print("Checking air company records with different filters...")
            
                # Check records with different Ativo/Excluido combinations
                air_all = self.session.query(AirCompanyInvoiceReport).all()
                air_ativo_true = self.session.query(AirCompanyInvoiceReport).filter(AirCompanyInvoiceReport.Ativo == True).all()
                air_excluido_false = self.session.query(AirCompanyInvoiceReport).filter(AirCompanyInvoiceReport.Excluido == False).all()
            
                print(f"  All air records: {len(air_all)}")
                print(f"  Air records with Ativo=True: {len(air_ativo_true)}")
                print(f"  Air records with Excluido=False: {len(air_excluido_false)}")
            
                if air_all:
                    sample = air_all[0]
                    print(f"  Sample air record - Ativo: {sample.Ativo}, Excluido: {sample.Excluido}")
        
            # Check if we have no catering records
            if len(catering_records) == 0:
                print("❌ WARNING: No active catering records found!")
                print("Checking catering records with different filters...")
            
                # Check records with different Ativo/Excluido combinations
                cat_all = self.session.query(CateringInvoiceReport).all()
                cat_ativo_true = self.session.query(CateringInvoiceReport).filter(CateringInvoiceReport.Ativo == True).all()
                cat_excluido_false = self.session.query(CateringInvoiceReport).filter(CateringInvoiceReport.Excluido == False).all()
            
                print(f"  All catering records: {len(cat_all)}")
                print(f"  Catering records with Ativo=True: {len(cat_ativo_true)}")
                print(f"  Catering records with Excluido=False: {len(cat_excluido_false)}")
            
                if cat_all:
                    sample = cat_all[0]
                    print(f"  Sample catering record - Ativo: {sample.Ativo}, Excluido: {sample.Excluido}")
        
            # If no air records, use all air records regardless of Ativo/Excluido
            if len(air_records) == 0:
                print("Using all air records regardless of Ativo/Excluido flags...")
                air_records = self.session.query(AirCompanyInvoiceReport).all()
                print(f"Now using {len(air_records)} air records")
        
            # If no catering records, use all catering records regardless of Ativo/Excluido  
            if len(catering_records) == 0:
                print("Using all catering records regardless of Ativo/Excluido flags...")
                catering_records = self.session.query(CateringInvoiceReport).all()
                print(f"Now using {len(catering_records)} catering records")
        
            # Debug: Show sample records
            if air_records:
                sample_air = air_records[0]
                print(f"\nSample Air Record:")
                print(f"  ID: {sample_air.Id}")
                print(f"  FlightDate: {sample_air.FlightDate}")
                print(f"  FlightNo: {sample_air.FlightNo}")
                print(f"  FlightNoRed: {sample_air.FlightNoRed}")
                print(f"  Class: {sample_air.Class}")
                print(f"  ServiceCode: {sample_air.ServiceCode}")
                print(f"  Dep: {sample_air.Dep}")
                print(f"  Arr: {sample_air.Arr}")
                print(f"  Ativo: {sample_air.Ativo}")
                print(f"  Excluido: {sample_air.Excluido}")
            else:
                print("❌ No air records available for processing!")
        
            if catering_records:
                sample_cat = catering_records[0]
                print(f"\nSample Catering Record:")
                print(f"  ID: {sample_cat.Id}")
                print(f"  FltDate: {sample_cat.FltDate}")
                print(f"  FltNo: {sample_cat.FltNo}")
                print(f"  Class: {sample_cat.Class}")
                print(f"  AlBillCode: {sample_cat.AlBillCode}")
                print(f"  Facility: {sample_cat.Facility}")
                print(f"  ItemDesc: {sample_cat.ItemDesc}")
                print(f"  Ativo: {sample_cat.Ativo}")
                print(f"  Excluido: {sample_cat.Excluido}")
            else:
                print("❌ No catering records available for processing!")
        
            # If we still don't have both types of records, return early
            if len(air_records) == 0 and len(catering_records) == 0:
                return {
                    "success": False,
                    "message": "No records found in either AirCompanyInvoiceReport or CateringInvoiceReport tables"
                }
        
            # Create lookup dictionaries for catering records with different matching strategies
            print("\n=== Creating Catering Lookup Tables ===")
            catering_by_date = {}
            catering_by_date_class = {}
            catering_by_date_facility = {}
        
            for i, cat_record in enumerate(catering_records):
                if i < 5:  # Only log first 5 to avoid spam
                    print(f"Processing catering record {i+1}/{len(catering_records)}: FltNo={cat_record.FltNo}, Date={cat_record.FltDate}, Class={cat_record.Class}")
            
                # Group by date only
                if cat_record.FltDate:
                    date_key = cat_record.FltDate
                    if date_key not in catering_by_date:
                        catering_by_date[date_key] = []
                    catering_by_date[date_key].append(cat_record)
                
                    # Group by date and class
                    if cat_record.Class:
                        date_class_key = (cat_record.FltDate, cat_record.Class.upper())
                        if date_class_key not in catering_by_date_class:
                            catering_by_date_class[date_class_key] = []
                        catering_by_date_class[date_class_key].append(cat_record)
                
                    # Group by date and facility (additional matching strategy)
                    if cat_record.Facility:
                        date_facility_key = (cat_record.FltDate, cat_record.Facility)
                        if date_facility_key not in catering_by_date_facility:
                            catering_by_date_facility[date_facility_key] = []
                        catering_by_date_facility[date_facility_key].append(cat_record)
        
            print(f"\nLookup tables created:")
            print(f"  By date: {len(catering_by_date)} unique dates")
            print(f"  By date+class: {len(catering_by_date_class)} unique date+class combinations")
            print(f"  By date+facility: {len(catering_by_date_facility)} unique date+facility combinations")
        
            # Process air company records
            print(f"\n=== Processing {len(air_records)} Air Company Records ===")
            processed_catering_records = set()
            reconciliation_records = []
            matched_count = 0
            air_only_count = 0
        
            for i, air_record in enumerate(air_records):
                if i < 5 or i % 1000 == 0:  # Log first 5 and every 1000th record
                    print(f"\nProcessing air record {i+1}/{len(air_records)}: {air_record.FlightNo}")
                    print(f"  FlightDate: {air_record.FlightDate}")
                    print(f"  Class: {air_record.Class}")
                    print(f"  Dep: {air_record.Dep}")
                    print(f"  Arr: {air_record.Arr}")
            
                matched = False
            
                # Strategy 1: Match by date and class
                if air_record.FlightDate and air_record.Class:
                    date_class_key = (air_record.FlightDate, air_record.Class.upper())
                
                    if date_class_key in catering_by_date_class:
                        available_catering = [
                            cat for cat in catering_by_date_class[date_class_key]
                            if id(cat) not in processed_catering_records
                        ]
                    
                        if available_catering:
                            cat_record = available_catering[0]
                            recon_record = self._create_matched_reconciliation_record(air_record, cat_record)
                            reconciliation_records.append(recon_record)
                            matched_count += 1
                            processed_catering_records.add(id(cat_record))
                            matched = True
                            if i < 5:
                                print(f"  ✅ MATCHED by date+class: Air {air_record.FlightNo} with Cat {cat_record.FltNo}")
            
                # Strategy 2: Match by date only
                if not matched and air_record.FlightDate:
                    if air_record.FlightDate in catering_by_date:
                        available_catering = [
                            cat for cat in catering_by_date[air_record.FlightDate]
                            if id(cat) not in processed_catering_records
                        ]
                    
                        if available_catering:
                            cat_record = available_catering[0]
                            recon_record = self._create_matched_reconciliation_record(air_record, cat_record)
                            reconciliation_records.append(recon_record)
                            matched_count += 1
                            processed_catering_records.add(id(cat_record))
                            matched = True
                            if i < 5:
                                print(f"  ✅ MATCHED by date only: Air {air_record.FlightNo} with Cat {cat_record.FltNo}")
            
                # If no match found, create air-only record
                if not matched:
                    recon_record = self._create_air_only_reconciliation_record(air_record)
                    reconciliation_records.append(recon_record)
                    air_only_count += 1
                    if i < 5:
                        print(f"  ❌ NO MATCH FOUND - Creating air-only record for {air_record.FlightNo}")
        
            # Process remaining catering records (catering only)
            print(f"\n=== Processing Remaining Catering Records ===")
            catering_only_count = 0
            for cat_record in catering_records:
                if id(cat_record) not in processed_catering_records:
                    recon_record = self._create_catering_only_reconciliation_record(cat_record)
                    reconciliation_records.append(recon_record)
                    catering_only_count += 1
        
            print(f"Processed {len(processed_catering_records)} catering records")
            print(f"Remaining catering-only records: {catering_only_count}")
        
            # Bulk insert all reconciliation records
            print(f"\n=== Saving {len(reconciliation_records)} Reconciliation Records ===")
            if reconciliation_records:
                self.session.bulk_save_objects(reconciliation_records)
                print("Bulk save completed")
        
            # Calculate differences for matched records
            print("=== Calculating Differences ===")
            self._calculate_reconciliation_differences()
        
            # Commit all changes
            self.session.commit()
            print("Database commit completed")
        
            total_records = len(reconciliation_records)
        
            print(f"\n=== FINAL SUMMARY ===")
            print(f"Total records created: {total_records}")
            print(f"Matched records: {matched_count}")
            print(f"Air-only records: {air_only_count}")
            print(f"Catering-only records: {catering_only_count}")
        
            print(f"Air-only records: {air_only_count}")
            print(f"Catering-only records: {catering_only_count}")
        
            return {
                "success": True,
                "message": "Reconciliation table populated successfully",
                "summary": {
                    "total_records": total_records,
                    "matched_records": matched_count,
                    "catering_only_records": catering_only_count,
                    "air_only_records": air_only_count,
                },
            }

        except Exception as e:
            self.session.rollback()
            print(f"❌ ERROR in populate_reconciliation_table: {str(e)}")
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
                .filter(
                    Reconciliation.Air == "Yes",
                    Reconciliation.Cat == "Yes"
                )
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
            AirQty=str(air_record.Qty) if air_record.Qty is not None else '0',
            AirUnitPrice=str(air_record.UnitPrice) if air_record.UnitPrice is not None else '0',
            AirSubTotal=str(air_record.SubTotal) if air_record.SubTotal is not None else '0.00',
            AirTax=str(air_record.Tax) if air_record.Tax is not None else '0.00',
            AirTotalIncTax=str(air_record.TotalIncTax) if air_record.TotalIncTax is not None else '0.00',
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
            Air='Yes',
            Cat='Yes'
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
            AirQty=str(air_record.Qty) if air_record.Qty is not None else '0',
            AirUnitPrice=str(air_record.UnitPrice) if air_record.UnitPrice is not None else '0',
            AirSubTotal=str(air_record.SubTotal) if air_record.SubTotal is not None else '0.00',
            AirTax=str(air_record.Tax) if air_record.Tax is not None else '0.00',
            AirTotalIncTax=str(air_record.TotalIncTax) if air_record.TotalIncTax is not None else '0.00',
            AirCurrency=air_record.Currency,
            AirItemStatus=air_record.ItemStatus,
            AirInvoiceStatus=air_record.InvoiceStatus,
            AirInvoiceDate=air_record.InvoiceDate,
            AirPaidDate=air_record.PaidDate,
            AirFlightNoRed=air_record.FlightNoRed,
        
            # Flags
            Air='Yes',
            Cat='No'
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
            Air='No',
            Cat='Yes'
        )
