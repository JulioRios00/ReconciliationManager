#Repositories
from repositories.repository import Repository
from typing import List, Dict
from decimal import Decimal
from datetime import datetime
#Tables
from models.schema_ccs import Flight, Configuration, FlightDate, DataSourc, PriceReport, InvoiceHistory
# Application-Specific Common Utilities
from common.custom_exception import CustomException

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
        super().__init__(db_session, DataSourc)

    def insert_data_source(self, file_name, page_number, id_fligth):
        data_source = DataSourc(source = file_name, page = page_number, id_fligth = id_fligth)
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

    def insert_packeg_price_report(self, facility, organization, pulled_date, run_date, report_table_data):
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
        price_report = self.session.query(PriceReport).filter(PriceReport.Id == id).first()
        if not price_report:
            raise CustomException(f"PriceReport with ID {id} not found")
        
        # Commit changes to the database
        self.session.delete(price_report)
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
