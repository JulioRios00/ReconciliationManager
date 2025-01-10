# Standard Library Imports
from datetime import datetime

# Application-Specific Repository Layer Imports
from repositories.ccs_repository import (
    FlightRepository,
    ConfigurationRepository,
    FlightDateRepository,
    SourceRepository,
    PriceReportRepository
)

# Application-Specific Service Layer Imports
from services.american_airline_service import extract_data
from services.price_report_service import price_report_data

# Application-Specific Common Utilities
from common.custom_exception import CustomException

class FlightService:
    def __init__(self, db_session):
        self.flight_repository = FlightRepository(db_session)
        self.configuration_repository = ConfigurationRepository(db_session)
        self.flight_date_repository = FlightDateRepository(db_session)
        self.data_source_repository = SourceRepository(db_session)


    def process_pdf_and_store(self, pdf_file, bucket, key):
        try:
            extracted_data = extract_data(pdf_file, bucket)
            # flights_to_insert = []

            for page, data in extracted_data.items():
                flight_data = data.get("flight_data")
                service_data = data.get("service_data")
                page_number = int(page.split()[1])
                
                if flight_data:
                    id_fligth = self.flight_repository.insert_flight(flight_data)
                    if id_fligth:
                        self.data_source_repository.insert_data_source(key, page_number, id_fligth)
                        date_strs = flight_data.get("datas", "").split(", ")
                        for date_str in date_strs:
                            try:
                                date_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
                                self.flight_date_repository.insert_flight_date(date_obj, id_fligth)
                            except Exception as e:
                                print(f"Error parsing or inserting date {date_str}: {e}")

                        if service_data:
                            self.configuration_repository.insert_configuration(service_data, id_fligth)
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
            for report in price_data:
                facility = facility,
                organization = organization,
                pulled_date = pulled_date,
                run_date = run_date,
                fac_org = report.get("FAC_ORG"),
                spc_nr = report.get("SPC_NR"),
                spc_dsc = report.get("SPC_DSC"),
                act_cat_nm = report.get("ACT_CAT_NM"),
                prs_sts_cd = report.get("PRS_STS_CD"),
                prc_eff_dt = report.get("PRC_EFF_DT"),
                prc_dis_dt = report.get("PRC_DIS_DT"),
                prc_cur_cd = report.get("PRC_CUR_CD"),
                tot_amt = report.get("TOT_AMT"),
                lbr_amt = report.get("LBR_AMT"),
                pkt_nr = report.get("PKT_NR"),
                pkt_nm = report.get("PKT_NM"),
                if not self.check_item(facility, organization, pulled_date, run_date, fac_org, spc_nr, spc_dsc, act_cat_nm, prs_sts_cd, prc_eff_dt, prc_dis_dt, prc_cur_cd, tot_amt, lbr_amt, pkt_nr, pkt_nm):
                    self.price_report_repository.insert_price_report(facility, organization, pulled_date, run_date, fac_org, spc_nr, spc_dsc, act_cat_nm, prs_sts_cd, prc_eff_dt, prc_dis_dt, prc_cur_cd, tot_amt, lbr_amt, pkt_nr, pkt_nm)
                else:
                    print(f"Item already exists: {report}")
        except Exception as e:
            print(f"Error processing price report data: {e}")

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