# Standard Library Imports
from datetime import datetime

# Application-Specific Repository Layer Imports
from repositories.ccs_repository import (
    FlightRepository,
    ConfigurationRepository,
    FlightDateRepository,
    SourceRepository,
    PriceReportRepository,
    InvoiceRepository
)

# Application-Specific Service Layer Imports
from services.airline_service import extract_data
from services.price_report_service import price_report_data
from services.invoices_service import analyze_invoices_data

# Application-Specific Common Utilities
from common.custom_exception import CustomException

class FlightService:
    def __init__(self, db_session):
        self.flight_repository = FlightRepository(db_session)
        self.configuration_repository = ConfigurationRepository(db_session)
        self.flight_date_repository = FlightDateRepository(db_session)
        self.data_source_repository = SourceRepository(db_session)


    def process_pdf_and_store(self, pdf_file, bucket, file_name):
        try:
            extracted_data = extract_data(pdf_file, bucket)
            # flights_to_insert = []

            for page, data in extracted_data.items():
                flight_data = data.get("flight_data")
                service_data = data.get("service_data")
                page_number = int(page.split()[1])
                
                if flight_data:
                    airline_company=flight_data.get("Empresa Aérea"),
                    period=flight_data.get("periodo"),
                    unit=flight_data.get("unidade"),
                    cycle=int(flight_data.get("ciclo", 0)),
                    vr_voo=int(flight_data.get("Vr Voo", 0)),
                    origin=flight_data.get("origem"),
                    destination=flight_data.get("destino"),
                    departure_time=flight_data.get("hora partida"),
                    arrival_time=flight_data.get("hora chegada"),
                    aircraft=int(flight_data.get("aeronave", 0)),
                    id_fligth = self.flight_repository.insert_flight(airline_company, period, unit, cycle, vr_voo, origin, destination, departure_time, arrival_time, aircraft)
                    if id_fligth:
                        self.data_source_repository.insert_data_source(file_name, page_number, id_fligth)
                        date_strs = flight_data.get("datas", "").split(", ")
                        for date_str in date_strs:
                            try:
                                date_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
                                self.flight_date_repository.insert_flight_date(date_obj, id_fligth)
                            except Exception as e:
                                print(f"Error parsing or inserting date {date_str}: {e}")

                        if service_data:
                            for class_type, packets in service_data.items():
                                for packet, packet_content in packets.items():
                                    destino_packet = packet_content.get("destino", "")
                                    items = packet_content.get("items", [])
                                    for item in items:
                                        packet=packet
                                        destination_packet=destino_packet
                                        item_code=item.get("Item Code", "")
                                        discription=item.get("Descrição", "")
                                        Provision_1=item.get("Provision_1", "")
                                        Provision_2=item.get("Provision_2", "")
                                        item_type=item.get("type", "")
                                        svc=int(item.get("Svc", "0"))

                                        self.configuration_repository.insert_configuration(class_type, packet, destination_packet, item_code, discription, Provision_1, Provision_2, item_type, svc, id_fligth)

        except Exception as e:
            print(f"Error processing flight data for page {page_number}: {e}")

class PriceReportService:
    def __init__(self, db_session):
        self.price_report_repository = PriceReportRepository(db_session)

    def process_price_report(self, data):
        try:
            header_data, price_data = price_report_data(data)
            facility = header_data.get("Line 2", "").split(": ", 1)[-1]
            organization = header_data.get("Line 3", "").split(": ", 1)[-1]
            pulled_date = header_data.get("Line 4", "").split("from ", 1)[-1].split(" to ")[0]
            run_date = header_data.get("Line 5", "").split(": ", 1)[-1]
            self.price_report_repository.insert_packeg_ackeg_price_report(facility, organization, pulled_date, run_date, price_data)
        except Exception as e:
            print(f"Error processing price report data: {e}")
        # try:
        #     header_data, price_data = price_report_data(data)
        #     facility = header_data.get("Line 2", "").split(": ", 1)[-1]
        #     organization = header_data.get("Line 3", "").split(": ", 1)[-1]
        #     pulled_date = header_data.get("Line 4", "").split("from ", 1)[-1].split(" to ")[0]
        #     run_date = header_data.get("Line 5", "").split(": ", 1)[-1]
        #     for report in price_data:
        #         facility = facility
        #         organization = organization
        #         pulled_date = pulled_date
        #         run_date = run_date
        #         fac_org = report.get("FAC_ORG")
        #         spc_nr = report.get("SPC_NR")
        #         spc_dsc = report.get("SPC_DSC")
        #         act_cat_nm = report.get("ACT_CAT_NM")
        #         prs_sts_cd = report.get("PRS_STS_CD")
        #         prc_eff_dt = report.get("PRC_EFF_DT")
        #         prc_dis_dt = report.get("PRC_DIS_DT")
        #         prc_cur_cd = report.get("PRC_CUR_CD")
        #         tot_amt = report.get("TOT_AMT")
        #         lbr_amt = report.get("LBR_AMT")
        #         pkt_nr = report.get("PKT_NR")
        #         pkt_nm = report.get("PKT_NM")
        #         self.price_report_repository.insert_price_report(facility, organization, pulled_date, run_date, fac_org, spc_nr, spc_dsc, act_cat_nm, prs_sts_cd, prc_eff_dt, prc_dis_dt, prc_cur_cd, tot_amt, lbr_amt, pkt_nr, pkt_nm)

                # if not self.check_item(facility, organization, pulled_date, run_date, fac_org, spc_nr, spc_dsc, act_cat_nm, prs_sts_cd, prc_eff_dt, prc_dis_dt, prc_cur_cd, tot_amt, lbr_amt, pkt_nr, pkt_nm):
                #     self.price_report_repository.insert_price_report(facility, organization, pulled_date, run_date, fac_org, spc_nr, spc_dsc, act_cat_nm, prs_sts_cd, prc_eff_dt, prc_dis_dt, prc_cur_cd, tot_amt, lbr_amt, pkt_nr, pkt_nm)
                # else:
                #     print(f"Item already exists: {report}")
        # except Exception as e:
        #     print(f"Error processing price report data: {e}")

    def delete_price_report(self, id):
        try:
            return self.price_report_repository.delete_price_report(id)
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error deleting price report: {e}")
            raise CustomException("an error occurred while deleting the PriceReport")
        
    def search_price_report(self, id=None, spc_dsc=None):
        try:
            if spc_dsc:
                return self.price_report_repository.get_by_spc_dsc(spc_dsc)
            elif id:
                return self.price_report_repository.get_by_id(id)
            else:
                raise CustomException("Either 'id' or 'SpcDsc' must be provided.")
        except Exception as e:
            print(f"Error find price report: {e}")

    def check_item(self, facility, organization, pulled_date, run_date, fac_org, spc_nr, spc_dsc, 
                act_cat_nm, prs_sts_cd, prc_eff_dt, prc_dis_dt, prc_cur_cd, tot_amt, lbr_amt, 
                pkt_nr, pkt_nm):
        try:
            return self.price_report_repository.check_item(facility, organization, pulled_date, run_date, fac_org, spc_nr, spc_dsc, 
                act_cat_nm, prs_sts_cd, prc_eff_dt, prc_dis_dt, prc_cur_cd, tot_amt, lbr_amt, 
                pkt_nr, pkt_nm)
        except Exception as e:
            print(f"Error find price report: {e}")

class InvoiceService:
    def __init__(self, db_session):
        self.invoice_repository = InvoiceRepository(db_session)

    def process_invoice(self, data, filename):
        try:
            invoice_data = analyze_invoices_data(data)
            self.invoice_repository.insert_packeg_invoice(invoice_data, filename)
        except Exception as e:
            print(f"Error processing invoice data: {e}")

    def delete_invoice_file(self, filename):
        try:
            return self.invoice_repository.delete_invoices(filename)
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error deleting invoice: {e}")
            raise CustomException("an error occurred while deleting the invoice history")