#Repositories
from repositories.repository import Repository
from typing import List, Dict
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

import logging
import os
#Tables
from models.schema_ccs import (
    Flight,
    Configuration,
    FlightDate,
    DataSource,
    PriceReport,
    InvoiceHistory,
    CateringInvoiceReport,
    AirCompanyInvoiceReport,
    Reconciliation
)
# Application-Specific Common Utilities
from common.custom_exception import CustomException

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'))
logger = logging.getLogger()
class FlightRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, Flight)       
        
    def insert_flight(self, airline_company, period, unit, cycle, vr_voo, origin, destination, departure_time, arrival_time, aircraft):
        """
        Inserts a new flight record into the Flight table.
        """
        flight = Flight(
            empresa_aerea=airline_company,
            periodo=period,
            unidade=unit,
            ciclo=cycle,
            vr_voo=vr_voo,
            origem=origin,
            destino=destination,
            hora_partida=departure_time,
            hora_chegada=arrival_time,
            aeronave=aircraft
        )
        self.session.add(flight)
        self.session.commit()
        print(f"Successfully inserted new flights into the database.")
        return flight.Id


    def flight_exists(self, flight_data):
        """
        Checks if a flight already exists in the database.
        """
        # Assuming 'flight_table' is your table where flights are stored
        filters = {getattr(Flight, key.lower()): value for key, value in flight_data.items() if hasattr(Flight, key.lower())}
        
        # Query the database with all filters
        result = self.db_session.query(Flight).filter_by(**filters).first()
        print("the data is existed")
        return result is not None
        
    def bulk_insert_flights(self, flights):
        """
        Inserts a list of flights into the database, excluding duplicates.
        """
        new_flights = [flight for flight in flights if not self.flight_exists(flight)]
        self.db_session.bulk_insert_mappings(Flight, new_flights)
        self.db_session.commit()
        print(f"Successfully inserted {len(new_flights)} new flights into the database.")

class ConfigurationRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, Configuration)

    def insert_configuration(self, class_type, packet, destination_packet, item_code, discription, Provision_1, Provision_2, item_type, svc, id_fligth):
        new_config = Configuration(
            tipo_de_classe=class_type,
            pacote=packet,
            destino_packet=destination_packet,
            código_doItem=item_code,
            descrição=discription,
            provision1=Provision_1,
            provision2=Provision_2,
            tipo=item_type,
            svc=svc,
            id_fligth=id_fligth
        )
        self.session.add(new_config)
        self.session.commit()
        print("Configuration data inserted successfully.")

    def check_configuration_item(self, class_type, packet, destination_packet, item_code, discription, Provision_1, Provision_2, item_type, svc):
        query = self.session.query(Configuration).filter(Configuration.Excluido == False)
        query = query.filter(
            Configuration.TipoDeClasse == class_type,
            Configuration.pacote == packet,
            Configuration.destinoPacket == destination_packet,
            Configuration.CódigoDoItem == item_code,
            Configuration.Descrição == discription,
            Configuration.Provision1 == Provision_1,
            Configuration.Provision2 == Provision_2,
            Configuration.Tipo == item_type,
            Configuration.Svc == svc
        )
        return query.first()
class FlightDateRepository(Repository):
    
    def __init__(self, db_session):
        super().__init__(db_session, FlightDate)

    def insert_flight_date(self, date, id_fligth):
        flight_date = FlightDate(date = date, id_fligth = id_fligth)
        self.session.add(flight_date)
        self.session.commit()
        print(f"Inserted flight date {date} for flight ID {id_fligth}")

class SourceRepository(Repository):
    
    def __init__(self, db_session):
        super().__init__(db_session, DataSource)

    def insert_data_source(self, file_name, page_number, id_fligth):
        data_source = DataSource(source = file_name, page = page_number, id_fligth = id_fligth)
        self.session.add(data_source)
        self.session.commit()
        print(f"Inserted data source for flight ID {id_fligth} from source {file_name} on page {page_number}")

class PriceReportRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, PriceReport)
        
    def insert_price_report(self, facility, organization, pulled_date, run_date, fac_org, spc_nr, spc_dsc, act_cat_nm, prs_sts_cd, prc_eff_dt, prc_dis_dt, prc_cur_cd, tot_amt, lbr_amt, pkt_nr, pkt_nm):
        new_report = PriceReport(
            facility = facility,
            organization = organization,
            pulled_date = pulled_date,
            run_date = run_date,
            fac_org = fac_org,
            spc_nr = spc_nr,
            spc_dsc = spc_dsc,
            act_cat_nm = act_cat_nm,
            prs_sts_cd = prs_sts_cd,
            prc_eff_dt = prc_eff_dt,
            prc_dis_dt = prc_dis_dt,
            prc_cur_cd = prc_cur_cd,
            tot_amt = tot_amt,
            lbr_amt = lbr_amt,
            pkt_nr = pkt_nr,
            pkt_nm = pkt_nm,
        )
        self.session.add(new_report)
        self.session.commit()
        print(f"Inserted new price report {new_report}")

    def insert_packeg_ackeg_price_report(self, facility, organization, pulled_date, run_date, report_table_data):
        for report in report_table_data:
            new_report = PriceReport(
                facility=facility,
                organization=organization,
                pulled_date=pulled_date,
                run_date=run_date,
                fac_org=report.get("FAC_ORG"),
                spc_nr=report.get("SPC_NR"),
                spc_dsc=report.get("SPC_DSC"),
                act_cat_nm=report.get("ACT_CAT_NM"),
                prs_sts_cd=report.get("PRS_STS_CD"),
                prc_eff_dt=report.get("PRC_EFF_DT"),
                prc_dis_dt=report.get("PRC_DIS_DT"),
                prc_cur_cd=report.get("PRC_CUR_CD"),
                tot_amt=report.get("TOT_AMT"),
                lbr_amt=report.get("LBR_AMT"),
                pkt_nr=report.get("PKT_NR"),
                pkt_nm=report.get("PKT_NM"),
            )
            self.session.add(new_report)
        self.session.commit()
        print(f"Inserted price reports")

    def delete_price_report(self, id):
        price_reports = self.session.query(PriceReport).filter(PriceReport.Id == id).first()
        if not price_reports:
            raise CustomException(f"PriceReport with ID {id} not found")
        # Commit changes to the database
        for report in price_reports:
            report.Excluido = True
        self.session.commit()
        return {'message': f'Deleted PriceReport id {id}'}

    def check_item(self, facility, organization, pulled_date, run_date, fac_org, spc_nr, spc_dsc, 
                act_cat_nm, prs_sts_cd, prc_eff_dt, prc_dis_dt, prc_cur_cd, tot_amt, lbr_amt, 
                pkt_nr, pkt_nm):
        query = self.session.query(PriceReport).filter(PriceReport.Excluido == False)
        query = query.filter(
            PriceReport.Facility == facility,
            PriceReport.Organization == organization,
            PriceReport.PulledDate == pulled_date,
            PriceReport.RunDate == run_date,
            PriceReport.FacOrg == fac_org,
            PriceReport.SpcNr == spc_nr,
            PriceReport.SpcDsc == spc_dsc,
            PriceReport.ActCatNm == act_cat_nm,
            PriceReport.PrsStsCd == prs_sts_cd,
            PriceReport.PrcEffDt == prc_eff_dt,
            PriceReport.PrcDisDt == prc_dis_dt,
            PriceReport.PrcCurCd == prc_cur_cd,
            PriceReport.TotAmt == tot_amt,
            PriceReport.LbrAmt == lbr_amt,
            PriceReport.PktNr == pkt_nr,
            PriceReport.PktNm == pkt_nm
        )
        return query.first()

    def get_by_id(self, id):
        return self.session.query(PriceReport).filter(PriceReport.Id == id, PriceReport.Excluido == False).first()

    def get_by_spc_dsc(self, spc_dsc):
        return self.session.query(PriceReport).filter(PriceReport.SpcDsc.ilike(f"%{spc_dsc}%"), PriceReport.Excluido == False).all()
    
class InvoiceRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, InvoiceHistory)

    def insert_packeg_invoice(self, invoice_data, FileName):
        for invoice in invoice_data:
            new_invoice = InvoiceHistory(
                brd_fac = invoice.get("Brd Fac"),
                brd_flt_dt = datetime.strptime(invoice.get("Brd Flt Dt"), "%Y-%m-%d") if invoice.get("Brd Flt Dt") else None,
                brd_flt_nr = int(invoice.get("Brd Flt Nr")) if invoice.get("Brd Flt Nr") else 0,
                op_cd = int(invoice.get("Op Cd")) if invoice.get("Op Cd") else 0,
                srv_dpt_sta_cd = invoice.get("Srv Dpt Sta Cd"),
                srv_arr_sta_cd = invoice.get("Srv Arr Sta Cd"),
                srv_flt_nr = int(invoice.get("Srv Flt Nr")) if invoice.get("Srv Flt Nr") else 0,
                srv_flt_dt = datetime.strptime(invoice.get("Srv Flt Dt"), "%Y-%m-%d") if invoice.get("Srv Flt Dt") else None,
                cos = invoice.get("Cos"),
                psg = int(invoice.get("Psg")) if invoice.get("Psg") else 0,
                meal = int(invoice.get("Meal")) if invoice.get("Meal") else 0,
                tray = int(invoice.get("Tray")) if invoice.get("Tray") else 0,
                total = Decimal(invoice.get("Total").replace(',', '')) if invoice.get("Total") else 0.00,
                paid = Decimal(invoice.get('Paid').replace(',', '')) if invoice.get('Paid') else 0.00,
                variance = Decimal(invoice.get("Variance").replace(',', '')) if invoice.get("Variance") else 0.00,
                grand_total = Decimal(invoice.get("Grand Total").replace(',', '')) if invoice.get("Grand Total") else 0.00,
                ovd_ind = invoice.get("Ovd Ind"),
                ivc_pcs_dt = datetime.strptime(invoice.get("Ivc Pcs Dt"), "%Y-%m-%d") if invoice.get("Ivc Pcs Dt") else None,
                ivc_dbs_dt = datetime.strptime(invoice.get("Ivc Dbs Dt"), "%Y-%m-%d") if invoice.get("Ivc Dbs Dt") else None,
                org = int(invoice.get("Org")) if invoice.get("Org") else 0,
                ivc_seq_nr = int(invoice.get("Ivc Seq Nr")) if invoice.get("Ivc Seq Nr") else 0,
                ivc_cre_dt = datetime.strptime(invoice.get("Ivc Cre Dt"), "%Y-%m-%d") if invoice.get("Ivc Cre Dt") else None,
                comments = invoice.get("Comments"),
                line_seq_nr = int(invoice.get("Line Seq Nr")) if invoice.get("Line Seq Nr") else None,
                item = int(invoice.get("Item")) if invoice.get("Item") else 0,
                act_amt = Decimal(invoice.get("Act Amt").replace(',', '')) if invoice.get("Act Amt") else 0.00,
                act_qty = int(invoice.get("Act Qty")) if invoice.get("Act Qty") else 0,
                sch_amt = Decimal(invoice.get("Sch Amt").replace(',', '')) if invoice.get("Sch Amt") else 0.00,
                sch_qty = int(invoice.get("Sch Qty")) if invoice.get("Sch Qty") else 0,
                act_lbr_amt = Decimal(invoice.get("Act Lbr Amt").replace(',', '')) if invoice.get("Act Lbr Amt") else 0.00,
                sch_lbr_amt = Decimal(invoice.get("Sch Lbr Amt").replace(',', '')) if invoice.get("Sch Lbr Amt") else 0.00,
                item_desc = invoice.get("Item Desc"),
                pkt_typ = invoice.get("Pkt Typ"),
                pkt_nr = int(invoice.get("Pkt Nr")) if invoice.get("Pkt Nr") else 0,
                pkt_nm = invoice.get("Pkt Nm"),
                pkt_var = int(invoice.get("Pkt Var")) if invoice.get("Pkt Var") else 0,
                file_name = FileName
            )
            self.session.add(new_invoice)
        self.session.commit()
        print(f"Inserted successfully invoice data")

    def delete_invoices(self, filename):
        invoices = self.session.query(InvoiceHistory).filter(InvoiceHistory.SourceName == filename).all()
        if not invoices:
            raise CustomException(f"invoice for {filename} not found")

        # Commit changes to the database
        for invoice in invoices:
            print(invoice)
            invoice.Excluido = True
        self.session.commit()
        return {'message': f'Deleted all {filename} invoices.'}


class CateringInvoiceRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, CateringInvoiceReport)

    def insert_billing_recon(
        self, facility=None, flt_date=None, flt_no=None, flt_inv=None,
        class_=None, item_group=None, itemcode=None, item_desc=None,
        al_bill_code=None, al_bill_desc=None, bill_catg=None, unit=None,
        pax=None, qty=None, unit_price=None, total_amount=None
    ):
        billing_recon = CateringInvoiceReport(
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
        self.session.add(billing_recon)
        self.session.commit()
        print(f"Inserted billing reconciliation record for flight {flt_no}")
        return billing_recon.Id

    def insert_package_billing_recon(self, billing_data, filename=None):
        for record in billing_data:
            billing_recon = CateringInvoiceReport(
                facility=record.get('facility'),
                flt_date=record.get('flt_date'),
                flt_no=record.get('flt_no'),
                flt_inv=record.get('flt_inv'),
                class_=record.get('class_'),
                item_group=record.get('item_group'),
                itemcode=record.get('itemcode'),
                item_desc=record.get('item_desc'),
                al_bill_code=record.get('al_bill_code'),
                al_bill_desc=record.get('al_bill_desc'),
                bill_catg=record.get('bill_catg'),
                unit=record.get('unit'),
                pax=record.get('pax'),
                qty=record.get('qty'),
                unit_price=record.get('unit_price'),
                total_amount=record.get('total_amount')
            )
            self.session.add(billing_recon)
            self.session.flush()
            print(f"{billing_recon.Id} has been successfully inserted")
        self.session.commit()

        print(f"Inserted {len(billing_data)} billing reconciliation records")
        return True

    def bulk_insert(self, model_instances):
        """
        Bulk insert CateringInvoiceReport instances
        """
        try:
            self.session.add_all(model_instances)
            self.session.commit()
            print(f"Successfully bulk inserted {len(model_instances)} records")
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error during bulk insert: {e}")
            raise e

    def delete_billing_recon(self, id):
        billing_recon = self.session.query(CateringInvoiceReport).filter(CateringInvoiceReport.Id == id).first()
        if not billing_recon:
            raise CustomException(f"CateringInvoiceReport with ID {id} not found")

        billing_recon.Excluido = True
        self.session.commit()
        return {'message': f'Deleted CateringInvoiceReport id {id}'}

    def delete_billing_recon_by_filename(self, filename):
        """
        Delete billing reconciliation records by source filename
        """
        billing_recons = self.session.query(CateringInvoiceReport).filter(
            CateringInvoiceReport.SourceFile == filename,
            CateringInvoiceReport.Excluido == False
        ).all()
        
        if not billing_recons:
            raise CustomException(f"No CateringInvoiceReport records found for filename {filename}")

        for billing_recon in billing_recons:
            billing_recon.Excluido = True
        
        self.session.commit()
        return {'message': f'Deleted {len(billing_recons)} CateringInvoiceReport records for filename {filename}'}

    def get_by_id(self, id):
        return self.session.query(CateringInvoiceReport).filter(
            CateringInvoiceReport.Id == id, 
            CateringInvoiceReport.Excluido == False
        ).first()

    def get_by_flight_no(self, flight_no):
        return self.session.query(CateringInvoiceReport).filter(
            CateringInvoiceReport.FltNo == flight_no, 
            CateringInvoiceReport.Excluido == False
        ).all()

    def get_by_facility(self, facility):
        return self.session.query(CateringInvoiceReport).filter(
            CateringInvoiceReport.Facility == facility,
            CateringInvoiceReport.Excluido == False
        ).all()

    def get_by_date_range(self, start_date, end_date):
        return self.session.query(CateringInvoiceReport).filter(
            CateringInvoiceReport.FltDate >= start_date,
            CateringInvoiceReport.FltDate <= end_date,
            CateringInvoiceReport.Excluido == False
        ).all()

    def get_all_active(self):
        return self.session.query(CateringInvoiceReport).filter(
            CateringInvoiceReport.Excluido == False
        ).all()

    def check_duplicate_record(self, facility, flt_date, flt_no, itemcode, al_bill_code):
        """
        Check if a record with the same key fields already exists
        """
        return self.session.query(CateringInvoiceReport).filter(
            CateringInvoiceReport.Facility == facility,
            CateringInvoiceReport.FltDate == flt_date,
            CateringInvoiceReport.FltNo == flt_no,
            CateringInvoiceReport.Itemcode == itemcode,
            CateringInvoiceReport.AlBillCode == al_bill_code,
            CateringInvoiceReport.Excluido == False
        ).first()


class AirCompanyInvoiceRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, AirCompanyInvoiceReport)

    def bulk_insert(self, model_instances):
        """
        Bulk insert AirCompanyInvoiceReport instances
        """
        try:
            self.session.add_all(model_instances)
            self.session.commit()
            print(f"Successfully bulk inserted {len(model_instances)} records")
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error during bulk insert: {e}")
            raise e

    def insert_erp_invoice_report(
        self, supplier=None, flight_date=None, flight_no=None, dep=None,
        arr=None, class_=None, invoiced_pax=None, service_code=None,
        supplier_code=None, service_description=None, aircraft=None,
        qty=None, unit_price=None, sub_total=None, tax=None,
        total_inc_tax=None, currency=None, item_status=None,
        invoice_status=None, invoice_date=None, paid_date=None,
        flight_no_red=None
    ):
        erp_invoice = AirCompanyInvoiceReport(
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
        self.session.add(erp_invoice)
        self.session.commit()
        print(f"Inserted ERP invoice report for flight {flight_no}")
        return erp_invoice.Id

    def insert_air_company_invoice(self, invoice_data, filename=None):
        inserted_count = 0
        for record in invoice_data:
            # Check if record exists based on key fields
            existing_record = self.session.query(AirCompanyInvoiceReport).filter(
                AirCompanyInvoiceReport.FlightNo == record.get('FlightNo'),
                AirCompanyInvoiceReport.FlightDate == record.get('FlightDate'),
                AirCompanyInvoiceReport.ServiceCode == record.get('ServiceCode'),
                AirCompanyInvoiceReport.Excluido.is_(False)
            ).first()

            if not existing_record:
                erp_invoice = AirCompanyInvoiceReport(
                    supplier=record.get('Supplier'),
                    flight_date=record.get('FlightDate'),
                    flight_no=record.get('FlightNo'),
                    dep=record.get('Dep'),
                    arr=record.get('Arr'),
                    class_=record.get('Class'),
                    invoiced_pax=record.get('InvoicedPax'),
                    service_code=record.get('ServiceCode'),
                    supplier_code=record.get('SupplierCode'),
                    service_description=record.get('ServiceDescription'),
                    aircraft=record.get('Aircraft'),
                    qty=record.get('Qty'),
                    unit_price=record.get('UnitPrice'),
                    sub_total=record.get('SubTotal'),
                    tax=record.get('Tax'),
                    total_inc_tax=record.get('TotalIncTax'),
                    currency=record.get('Currency'),
                    item_status=record.get('ItemStatus'),
                    invoice_status=record.get('InvoiceStatus'),
                    invoice_date=record.get('InvoiceDate'),
                    paid_date=record.get('PaidDate'),
                    flight_no_red=record.get('FlightNoRed')
                )
                self.session.add(erp_invoice)
                inserted_count += 1

        self.session.commit()
        print(f"Inserted {inserted_count} new ERP invoice reports")
        return True

    def delete_erp_invoice(self, id):
        erp_invoice = self.session.query(AirCompanyInvoiceReport).filter(AirCompanyInvoiceReport.Id == id).first()
        if not erp_invoice:
            raise CustomException(f"AirCompanyInvoiceReport with ID {id} not found")

        erp_invoice.Excluido = True
        self.session.commit()
        return {'message': f'Deleted AirCompanyInvoiceReport id {id}'}

    def get_by_id(self, id):
        return self.session.query(AirCompanyInvoiceReport).filter(AirCompanyInvoiceReport.Id == id, AirCompanyInvoiceReport.Excluido.is_(False)).first()

    def get_by_flight_no(self, flight_no):
        return self.session.query(AirCompanyInvoiceReport).filter(AirCompanyInvoiceReport.FlightNo == flight_no, AirCompanyInvoiceReport.Excluido.is_(False)).all()


class ReconciliationRepository:
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger(__name__)  # This will now work
    
    def debug_database_content(self):
        """Debug method to see what's actually in the database"""
        try:
            # Get total count
            total_count = self.session.query(Reconciliation).count()
            self.logger.info(f"Total records in Reconciliation table: {total_count}")
            
            # Get first 5 records to see date formats
            sample_records = self.session.query(Reconciliation).limit(5).all()
            self.logger.info(f"Sample records found: {len(sample_records)}")
            
            for i, record in enumerate(sample_records):
                self.logger.info(f"Record {i+1}:")
                self.logger.info(f"  AirFlightDate: '{record.AirFlightDate}' (type: {type(record.AirFlightDate)})")
                self.logger.info(f"  CatFltDate: '{record.CatFltDate}' (type: {type(record.CatFltDate)})")
                self.logger.info(f"  AirFlightNo: '{record.AirFlightNo}'")
                
                # Extract just the date part to see what func.date() would return
                if record.AirFlightDate:
                    air_date_only = record.AirFlightDate.date() if hasattr(record.AirFlightDate, 'date') else record.AirFlightDate
                    self.logger.info(f"  AirFlightDate (date only): {air_date_only}")
                
                if record.CatFltDate:
                    cat_date_only = record.CatFltDate.date() if hasattr(record.CatFltDate, 'date') else record.CatFltDate
                    self.logger.info(f"  CatFltDate (date only): {cat_date_only}")
            
            # Check for any records in 2025
            records_2025 = self.session.query(Reconciliation).filter(
                func.extract('year', Reconciliation.AirFlightDate) == 2025
            ).count()
            self.logger.info(f"Records with AirFlightDate in 2025: {records_2025}")
            
            records_2025_cat = self.session.query(Reconciliation).filter(
                func.extract('year', Reconciliation.CatFltDate) == 2025
            ).count()
            self.logger.info(f"Records with CatFltDate in 2025: {records_2025_cat}")
            
            # Check for April 2025 specifically
            april_2025_air = self.session.query(Reconciliation).filter(
                func.extract('year', Reconciliation.AirFlightDate) == 2025,
                func.extract('month', Reconciliation.AirFlightDate) == 4
            ).count()
            self.logger.info(f"Records with AirFlightDate in April 2025: {april_2025_air}")
            
            april_2025_cat = self.session.query(Reconciliation).filter(
                func.extract('year', Reconciliation.CatFltDate) == 2025,
                func.extract('month', Reconciliation.CatFltDate) == 4
            ).count()
            self.logger.info(f"Records with CatFltDate in April 2025: {april_2025_cat}")
            
        except Exception as e:
            self.logger.error(f"Debug database content error: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

    def get_by_date_range(self, start_date, end_date, limit=None, offset=None):
        """
        Get reconciliation records filtered by FLIGHT DATE range with detailed logging
        """
        try:
            self.logger.info(f"=== get_by_date_range called ===")
            self.logger.info(f"start_date: {start_date} (type: {type(start_date)})")
            self.logger.info(f"end_date: {end_date} (type: {type(end_date)})")
            self.logger.info(f"limit: {limit}, offset: {offset}")
            
            # Debug database content first
            self.debug_database_content()
            
            # Test different query approaches
            self.logger.info("=== Testing different query approaches ===")
            
            # Approach 1: Using func.date()
            self.logger.info("Approach 1: Using func.date()")
            air_query_1 = self.session.query(Reconciliation).filter(
                func.date(Reconciliation.AirFlightDate) >= start_date,
                func.date(Reconciliation.AirFlightDate) <= end_date
            )
            air_count_1 = air_query_1.count()
            self.logger.info(f"Air records found with func.date(): {air_count_1}")
            
            cat_query_1 = self.session.query(Reconciliation).filter(
                func.date(Reconciliation.CatFltDate) >= start_date,
                func.date(Reconciliation.CatFltDate) <= end_date
            )
            cat_count_1 = cat_query_1.count()
            self.logger.info(f"Cat records found with func.date(): {cat_count_1}")
            
            # Approach 2: Using extract for year/month/day
            self.logger.info("Approach 2: Using extract for year/month/day")
            start_year, start_month, start_day = start_date.year, start_date.month, start_date.day
            end_year, end_month, end_day = end_date.year, end_date.month, end_date.day
            
            self.logger.info(f"Looking for dates between {start_year}-{start_month:02d}-{start_day:02d} and {end_year}-{end_month:02d}-{end_day:02d}")
            
            # For April 2025, let's check if there are any records in that month
            april_2025_query = self.session.query(Reconciliation).filter(
                func.extract('year', Reconciliation.AirFlightDate) == 2025,
                func.extract('month', Reconciliation.AirFlightDate) == 4
            )
            april_2025_count = april_2025_query.count()
            self.logger.info(f"Records in April 2025 (Air): {april_2025_count}")
            
            if april_2025_count > 0:
                # Get a sample record to see the actual date
                sample_april = april_2025_query.first()
                self.logger.info(f"Sample April 2025 record: AirFlightDate = {sample_april.AirFlightDate}")
            
            # Approach 3: Direct datetime comparison (convert dates to datetime)
            self.logger.info("Approach 3: Direct datetime comparison")
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            self.logger.info(f"Converted to datetime: {start_datetime} to {end_datetime}")
            
            air_query_3 = self.session.query(Reconciliation).filter(
                Reconciliation.AirFlightDate >= start_datetime,
                Reconciliation.AirFlightDate <= end_datetime
            )
            air_count_3 = air_query_3.count()
            self.logger.info(f"Air records found with datetime comparison: {air_count_3}")
            
            # Use the approach that finds records
            if air_count_1 > 0 or cat_count_1 > 0:
                self.logger.info("Using func.date() approach")
                combined_query = air_query_1.union(cat_query_1)
            elif air_count_3 > 0:
                self.logger.info("Using datetime comparison approach")
                cat_query_3 = self.session.query(Reconciliation).filter(
                    Reconciliation.CatFltDate >= start_datetime,
                    Reconciliation.CatFltDate <= end_datetime
                )
                combined_query = air_query_3.union(cat_query_3)
            else:
                self.logger.warning("No records found with any approach")
                return []
            
            # Apply ordering and pagination
            combined_query = combined_query.order_by(
                Reconciliation.AirFlightDate,
                Reconciliation.AirFlightNo
            )
            
            total_before_pagination = combined_query.count()
            self.logger.info(f"Total records before pagination: {total_before_pagination}")
            
            if offset is not None:
                combined_query = combined_query.offset(offset)
            if limit is not None:
                combined_query = combined_query.limit(limit)
                
            results = combined_query.all()
            self.logger.info(f"Final results returned: {len(results)}")
            
            # Log first result for verification
            if results:
                first_result = results[0]
                self.logger.info(f"First result: AirFlightDate={first_result.AirFlightDate}, AirFlightNo={first_result.AirFlightNo}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in get_by_date_range: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def get_count_by_date_range(self, start_date, end_date):
        """Get count of records in flight date range with logging"""
        try:
            self.logger.info(f"=== get_count_by_date_range called ===")
            self.logger.info(f"start_date: {start_date}, end_date: {end_date}")
            
            # Try the same approaches as get_by_date_range
            air_query = self.session.query(Reconciliation).filter(
                func.date(Reconciliation.AirFlightDate) >= start_date,
                func.date(Reconciliation.AirFlightDate) <= end_date
            )
            
            cat_query = self.session.query(Reconciliation).filter(
                func.date(Reconciliation.CatFltDate) >= start_date,
                func.date(Reconciliation.CatFltDate) <= end_date
            )
            
            air_count = air_query.count()
            cat_count = cat_query.count()
            
            self.logger.info(f"Air count: {air_count}, Cat count: {cat_count}")
            
            combined_query = air_query.union(cat_query)
            total_count = combined_query.count()
            
            self.logger.info(f"Total count after union: {total_count}")
            return total_count
            
        except Exception as e:
            self.logger.error(f"Error in get_count_by_date_range: {e}")
            return 0

    def get_filtered_by_date_range(self, filter_type, start_date, end_date, limit=None, offset=None):
        """
        Get filtered reconciliation records within flight date range with logging
        """
        try:
            self.logger.info(f"=== get_filtered_by_date_range called ===")
            self.logger.info(f"filter_type: {filter_type}, start_date: {start_date}, end_date: {end_date}")
            
            # Base queries for flight date filtering using date extraction
            air_base_query = self.session.query(Reconciliation).filter(
                func.date(Reconciliation.AirFlightDate) >= start_date,
                func.date(Reconciliation.AirFlightDate) <= end_date
            )
            
            cat_base_query = self.session.query(Reconciliation).filter(
                func.date(Reconciliation.CatFltDate) >= start_date,
                func.date(Reconciliation.CatFltDate) <= end_date
            )

            # Apply additional filters to both queries
            if filter_type == 'discrepancies':
                air_query = air_base_query.filter(
                    (Reconciliation.DifQty == 'Yes') | (Reconciliation.DifPrice == 'Yes')
                )
                cat_query = cat_base_query.filter(
                    (Reconciliation.DifQty == 'Yes') | (Reconciliation.DifPrice == 'Yes')
                )
            elif filter_type == 'quantity_difference':
                air_query = air_base_query.filter(Reconciliation.DifQty == 'Yes')
                cat_query = cat_base_query.filter(Reconciliation.DifQty == 'Yes')
            elif filter_type == 'price_difference':
                air_query = air_base_query.filter(Reconciliation.DifPrice == 'Yes')
                cat_query = cat_base_query.filter(Reconciliation.DifPrice == 'Yes')
            elif filter_type == 'air_only':
                air_query = air_base_query.filter(
                    Reconciliation.Air == 'Yes',
                    Reconciliation.Cat == 'No'
                )
                cat_query = cat_base_query.filter(
                    Reconciliation.Air == 'Yes',
                    Reconciliation.Cat == 'No'
                )
            elif filter_type == 'cat_only':
                air_query = air_base_query.filter(
                    Reconciliation.Air == 'No',
                    Reconciliation.Cat == 'Yes'
                )
                cat_query = cat_base_query.filter(
                    Reconciliation.Air == 'No',
                    Reconciliation.Cat == 'Yes'
                )
            else:
                air_query = air_base_query
                cat_query = cat_base_query

            air_count = air_query.count()
            cat_count = cat_query.count()
            self.logger.info(f"Filtered counts - Air: {air_count}, Cat: {cat_count}")

            # Union and apply pagination
            combined_query = air_query.union(cat_query).order_by(
                Reconciliation.AirFlightDate,
                Reconciliation.AirFlightNo
            )
            
            if offset is not None:
                combined_query = combined_query.offset(offset)
            if limit is not None:
                combined_query = combined_query.limit(limit)
                
            results = combined_query.all()
            self.logger.info(f"Filtered results returned: {len(results)}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in get_filtered_by_date_range: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def get_filtered_count_by_date_range(self, filter_type, start_date, end_date):
        """Get count of filtered records in flight date range with logging"""
        try:
            self.logger.info(f"=== get_filtered_count_by_date_range called ===")
            self.logger.info(f"filter_type: {filter_type}")
            
            # Base queries for flight date filtering
            air_base_query = self.session.query(Reconciliation).filter(
                func.date(Reconciliation.AirFlightDate) >= start_date,
                func.date(Reconciliation.AirFlightDate) <= end_date
            )
            
            cat_base_query = self.session.query(Reconciliation).filter(
                func.date(Reconciliation.CatFltDate) >= start_date,
                func.date(Reconciliation.CatFltDate) <= end_date
            )

            # Apply additional filters
            if filter_type == 'discrepancies':
                air_query = air_base_query.filter(
                    (Reconciliation.DifQty == 'Yes') | (Reconciliation.DifPrice == 'Yes')
                )
                cat_query = cat_base_query.filter(
                    (Reconciliation.DifQty == 'Yes') | (Reconciliation.DifPrice == 'Yes')
                )
            elif filter_type == 'quantity_difference':
                air_query = air_base_query.filter(Reconciliation.DifQty == 'Yes')
                cat_query = cat_base_query.filter(Reconciliation.DifQty == 'Yes')
            elif filter_type == 'price_difference':
                air_query = air_base_query.filter(Reconciliation.DifPrice == 'Yes')
                cat_query = cat_base_query.filter(Reconciliation.DifPrice == 'Yes')
            elif filter_type == 'air_only':
                air_query = air_base_query.filter(
                    Reconciliation.Air == 'Yes',
                    Reconciliation.Cat == 'No'
                )
                cat_query = cat_base_query.filter(
                    Reconciliation.Air == 'Yes',
                    Reconciliation.Cat == 'No'
                )
            elif filter_type == 'cat_only':
                air_query = air_base_query.filter(
                    Reconciliation.Air == 'No',
                    Reconciliation.Cat == 'Yes'
                )
                cat_query = cat_base_query.filter(
                    Reconciliation.Air == 'No',
                    Reconciliation.Cat == 'Yes'
                )
            else:
                air_query = air_base_query
                cat_query = cat_base_query

            # Count union results
            combined_query = air_query.union(cat_query)
            total_count = combined_query.count()
            self.logger.info(f"Filtered count result: {total_count}")
            return total_count
            
        except Exception as e:
            self.logger.error(f"Error in get_filtered_count_by_date_range: {e}")
            return 0

    def get_filtered(self, filter_type):
        """Get filtered reconciliation records"""
        query = self.session.query(Reconciliation)

        if filter_type == 'discrepancies':
            query = query.filter(
                (Reconciliation.DifQty == 'Yes') | (Reconciliation.DifPrice == 'Yes')
            )
        elif filter_type == 'quantity_difference':
            query = query.filter(Reconciliation.DifQty == 'Yes')
        elif filter_type == 'price_difference':
            query = query.filter(Reconciliation.DifPrice == 'Yes')
        elif filter_type == 'air_only':
            query = query.filter(
                Reconciliation.Air == 'Yes',
                Reconciliation.Cat == 'No'
            )
        elif filter_type == 'cat_only':
            query = query.filter(
                Reconciliation.Air == 'No',
                Reconciliation.Cat == 'Yes'
            )

        return query.order_by(
            Reconciliation.AirFlightDate,
            Reconciliation.AirFlightNo
        ).all()

    def get_filtered_count(self, filter_type):
        """Get count of filtered reconciliation records"""
        query = self.session.query(Reconciliation)

        if filter_type == 'discrepancies':
            query = query.filter(
                (Reconciliation.DifQty == 'Yes') | (Reconciliation.DifPrice == 'Yes')
            )
        elif filter_type == 'quantity_difference':
            query = query.filter(Reconciliation.DifQty == 'Yes')
        elif filter_type == 'price_difference':
            query = query.filter(Reconciliation.DifPrice == 'Yes')
        elif filter_type == 'air_only':
            query = query.filter(
                Reconciliation.Air == 'Yes',
                Reconciliation.Cat == 'No'
            )
        elif filter_type == 'cat_only':
            query = query.filter(
                Reconciliation.Air == 'No',
                Reconciliation.Cat == 'Yes'
            )

        return query.count()

    def get_filtered_paginated(self, filter_type, limit, offset):
        """
        Get filtered records with pagination applied at database level
        """
        query = self.session.query(Reconciliation)

        if filter_type == 'discrepancies':
            query = query.filter(
                (Reconciliation.DifQty == 'Yes') | (Reconciliation.DifPrice == 'Yes')
            )
        elif filter_type == 'quantity_difference':
            query = query.filter(Reconciliation.DifQty == 'Yes')
        elif filter_type == 'price_difference':
            query = query.filter(Reconciliation.DifPrice == 'Yes')
        elif filter_type == 'air_only':
            query = query.filter(
                Reconciliation.Air == 'Yes',
                Reconciliation.Cat == 'No'
            )
        elif filter_type == 'cat_only':
            query = query.filter(
                Reconciliation.Air == 'No',
                Reconciliation.Cat == 'Yes'
            )

        return query.order_by(
            Reconciliation.AirFlightDate,
            Reconciliation.AirFlightNo
        ).offset(offset).limit(limit).all()
