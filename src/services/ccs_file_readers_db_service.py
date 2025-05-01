from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from services.ccs_file_readers_service import (
    billing_inflair_invoice_report,
    billing_promeus_invoice_report,
    pricing_read_inflair,
    pricing_read_promeus_with_flight_classes
)
from src.models.schema_ccs import (
    Flight, PriceReport, DataSource, InvoiceHistory
)


def save_billing_inflair_to_db(file_path: str, db: Session) -> List[Dict[str, Any]]:
    """
    Read billing inflair data from Excel file and save to database using InvoiceHistory model
    """
    # Get data from the file
    data = billing_inflair_invoice_report(file_path)
    
    # Save each record to the database
    for item in data:
        # Map the data to InvoiceHistory model
        # Note: Field mapping will need to be adjusted based on actual data structure
        db_item = InvoiceHistory(
            brd_flt_nr=item.get("Number"),
            brd_flt_dt=item.get("Date"),
            srv_flt_dt=item.get("Date.1"),
            srv_flt_nr=item.get("Number.1"),
            cos=item.get("F"),  # This might need adjustment
            psg=item.get("Y"),  # This might need adjustment
            total=item.get("Total"),
            airline=item.get("Statement"),
            billing_reference=item.get("Period"),
            imported_at=datetime.now(),
            source_name=file_path,
            # Fill required fields with default values if they're not in the data
            op_cd=0,
            srv_dpt_sta_cd="",
            srv_arr_sta_cd="",
            ivc_pcs_dt=None,
            ivc_dbs_dt=None,
            org=0,
            ivc_seq_nr=0,
            ivc_cre_dt=None,
            comments="",
            line_seq_nr=0,
            item=0,
            act_amt=0,
            act_qty=0,
            sch_amt=0,
            sch_qty=0,
            act_lbr_amt=0,
            sch_lbr_amt=0,
            item_desc=""
        )
        db.add(db_item)
    
    db.commit()
    
    # Return the original data
    return data


def save_billing_promeus_to_db(file_path: str, db: Session) -> List[Dict[str, Any]]:
    """
    Read billing promeus data from Excel file and save to database using InvoiceHistory model
    """
    # Get data from the file
    data = billing_promeus_invoice_report(file_path)
    
    # Save each record to the database
    for item in data:
        # Map the data to InvoiceHistory model
        db_item = InvoiceHistory(
            airline=item.get("SUPPLIER"),
            brd_flt_dt=item.get("FLIGHT DATE"),
            brd_flt_nr=item.get("FLIGHT NO."),
            srv_dpt_sta_cd=item.get("DEP"),
            srv_arr_sta_cd=item.get("ARR"),
            imported_at=datetime.now(),
            source_name=file_path,
            # Fill required fields with default values
            op_cd=0,
            srv_flt_nr=0,
            srv_flt_dt=None,
            cos="",
            psg=0,
            meal=0,
            tray=0,
            total=0,
            paid=0,
            variance=0,
            grand_total=0,
            ovd_ind="",
            ivc_pcs_dt=None,
            ivc_dbs_dt=None,
            org=0,
            ivc_seq_nr=0,
            ivc_cre_dt=None,
            comments="",
            line_seq_nr=0,
            item=0,
            act_amt=0,
            act_qty=0,
            sch_amt=0,
            sch_qty=0,
            act_lbr_amt=0,
            sch_lbr_amt=0,
            item_desc=""
        )
        db.add(db_item)
    
    db.commit()
    
    # Return the original data
    return data


def save_pricing_inflair_to_db(file_path: str, db: Session) -> List[Dict[str, Any]]:
    """
    Read pricing inflair data from Excel file and save to database using PriceReport model
    """
    # Get data from the file
    data = pricing_read_inflair(file_path)
    
    # Save each record to the database
    for item in data:
        # Map the data to PriceReport model
        db_item = PriceReport(
            spc_nr=int(item.get("item_code")) if item.get("item_code") else 0,
            prc_eff_dt=item.get("start_date"),
            prc_dis_dt=item.get("end_date"),
            organization=item.get("airline_code"),
            prc_cur_cd=item.get("currency"),
            tot_amt=item.get("price"),
            pulled_date=item.get("created_date"),
            run_date=item.get("created_date"),
            source_file=file_path,
            # Fill required fields with default values
            facility="",
            fac_org="",
            spc_dsc="",
            act_cat_nm="",
            prs_sts_cd="",
            lbr_amt=0,
            pkt_nr=0,
            pkt_nm=""
        )
        db.add(db_item)

    db.commit()

    return data


def save_pricing_promeus_to_db(file_path: str, db: Session) -> Dict[str, List[Dict[str, Any]]]:
    """
    Read pricing promeus data from Excel file and save to database using PriceReport model
    """

    data = pricing_read_promeus_with_flight_classes(file_path)

    for class_name, items in data.items():
        for item in items:
            db_item = PriceReport(
                facility=item.get("facility"),
                spc_nr=int(item.get("service_code")) if item.get("service_code") else 0,
                spc_dsc=item.get("description"),
                prc_cur_cd=item.get("currency"),
                tot_amt=float(item.get("price")) if item.get("price") else 0,
                act_cat_nm=class_name,  
                source_file=file_path,
                pulled_date=datetime.now().strftime("%Y-%m-%d"),
                run_date=datetime.now().strftime("%Y-%m-%d"),

                organization="",
                fac_org="",
                prs_sts_cd="",
                prc_eff_dt=None,
                prc_dis_dt=None,
                lbr_amt=0,
                pkt_nr=0,
                pkt_nm=""
            )
            db.add(db_item)
    
    db.commit()
    
    # Return the original data
    return data


def create_flight_from_data(
    db: Session, 
    airline: str, 
    origin: str, 
    destination: str,
    flight_number: str,
    flight_date: str,
    source_file: str,
    page_number: int = 1
) -> Optional[Flight]:
    """
    Create a Flight record with associated DataSource
    """
    flight = Flight(
        empresa_aerea=airline,
        origem=origin,
        destino=destination,
        vr_voo=flight_number,
        data_voo=flight_date,
        periodo="",
        unidade="",
        ciclo=0,
        hora_partida="",
        hora_chegada="",
        aeronave=0
    )
    db.add(flight)
    db.flush()  # Flush to get the ID

    data_source = DataSource(
        source=source_file,
        page=page_number,
        id_flight=flight.Id
    )
    db.add(data_source)

    return flight
