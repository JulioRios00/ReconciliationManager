#Repositories
from repositories.repository import Repository
from typing import List, Dict
#Tables
from models.schema_ccs import Flight, Configuration, FlightDate, DataSourc

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
        print(file_name, page_number, id_fligth)
        data_source = DataSourc(source = file_name, page = page_number, id_fligth = id_fligth)
        self.session.add(data_source)
        self.session.commit()
        print(f"Inserted data source for flight ID {id_fligth} from source {file_name} on page {page_number}")