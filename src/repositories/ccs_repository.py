#Repositories
from repositories.repository import Repository
from typing import List, Dict
#Tables
from models.schema_ccs import Flight, Configuration, FlightDate, DataSourc, PriceReport
# Application-Specific Common Utilities
from common.custom_exception import CustomException

class FlightRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, Flight)       
        
    def insert_flight(self, flight_data: dict):
        """
        Inserts a new flight record into the Flight table.
        """
        flight = Flight(
            empresa_aerea=flight_data.get("Empresa Aérea"),
            periodo=flight_data.get("periodo"),
            unidade=flight_data.get("unidade"),
            ciclo=int(flight_data.get("ciclo", 0)),
            vr_voo=int(flight_data.get("Vr Voo", 0)),
            origem=flight_data.get("origem"),
            destino=flight_data.get("destino"),
            hora_partida=flight_data.get("hora partida"),
            hora_chegada=flight_data.get("hora chegada"),
            aeronave=int(flight_data.get("aeronave", 0)),
        )
        self.session.add(flight)
        self.session.commit()
        print(f"Successfully inserted {flight_data} new flights into the database.")
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

    def insert_configuration(self, service_data, flight_id):
        for class_type, packets in service_data.items():
            for packet, packet_content in packets.items():
                destino_packet = packet_content.get("destino", "")
                items = packet_content.get("items", [])
                for item in items:
                    new_config = Configuration(
                        tipo_de_classe=class_type,
                        pacote=packet,
                        destino_packet=destino_packet,
                        código_doItem=item.get("Item Code", ""),
                        descrição=item.get("Descrição", ""),
                        provision1=item.get("Provision_1", ""),
                        provision2=item.get("Provision_2", ""),
                        tipo=item.get("type", ""),
                        svc=int(item.get("Svc", "0")),
                        id_fligth=flight_id
                    )
                    self.session.add(new_config)
        self.session.commit()
        print("Configuration data inserted successfully.")

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