# Standard Library Imports
from datetime import datetime

# Application-Specific Repository Layer Imports
from repositories.ccs_repository import (
    FlightRepository,
    ConfigurationRepository,
    FlightDateRepository,
    SourceRepository,
    PriceReportRepository,
    InvoiceRepository,
    ErpInvoiceReportRepository,
    BillingReconRepository
)

from models.schema_ccs import (
    ErpInvoiceReport,
    BillingRecon
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
                    airline_company = (flight_data.get("Empresa Aérea"),)
                    period = (flight_data.get("periodo"),)
                    unit = (flight_data.get("unidade"),)
                    cycle = (int(flight_data.get("ciclo", 0)),)
                    vr_voo = (int(flight_data.get("Vr Voo", 0)),)
                    origin = (flight_data.get("origem"),)
                    destination = (flight_data.get("destino"),)
                    departure_time = (flight_data.get("hora partida"),)
                    arrival_time = (flight_data.get("hora chegada"),)
                    aircraft = (int(flight_data.get("aeronave", 0)),)
                    id_fligth = self.flight_repository.insert_flight(
                        airline_company,
                        period,
                        unit,
                        cycle,
                        vr_voo,
                        origin,
                        destination,
                        departure_time,
                        arrival_time,
                        aircraft,
                    )
                    if id_fligth:
                        self.data_source_repository.insert_data_source(
                            file_name, page_number, id_fligth
                        )
                        date_strs = flight_data.get("datas", "").split(", ")
                        for date_str in date_strs:
                            try:
                                date_obj = datetime.strptime(
                                    date_str, "%d/%m/%Y"
                                ).date()
                                self.flight_date_repository.insert_flight_date(
                                    date_obj, id_fligth
                                )
                            except Exception as e:
                                print(
                                    f"Error parsing or inserting date {date_str}: {e}"
                                )

                        if service_data:
                            for class_type, packets in service_data.items():
                                for packet, packet_content in packets.items():
                                    destino_packet = packet_content.get("destino", "")
                                    items = packet_content.get("items", [])
                                    for item in items:
                                        packet = packet
                                        destination_packet = destino_packet
                                        item_code = item.get("Item Code", "")
                                        discription = item.get("Descrição", "")
                                        Provision_1 = item.get("Provision_1", "")
                                        Provision_2 = item.get("Provision_2", "")
                                        item_type = item.get("type", "")
                                        svc = int(item.get("Svc", "0"))

                                        self.configuration_repository.insert_configuration(
                                            class_type,
                                            packet,
                                            destination_packet,
                                            item_code,
                                            discription,
                                            Provision_1,
                                            Provision_2,
                                            item_type,
                                            svc,
                                            id_fligth,
                                        )

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
            pulled_date = (
                header_data.get("Line 4", "").split("from ", 1)[-1].split(" to ")[0]
            )
            run_date = header_data.get("Line 5", "").split(": ", 1)[-1]
            self.price_report_repository.insert_packeg_ackeg_price_report(
                facility, organization, pulled_date, run_date, price_data
            )
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

    def check_item(
        self,
        facility,
        organization,
        pulled_date,
        run_date,
        fac_org,
        spc_nr,
        spc_dsc,
        act_cat_nm,
        prs_sts_cd,
        prc_eff_dt,
        prc_dis_dt,
        prc_cur_cd,
        tot_amt,
        lbr_amt,
        pkt_nr,
        pkt_nm,
    ):
        try:
            return self.price_report_repository.check_item(
                facility,
                organization,
                pulled_date,
                run_date,
                fac_org,
                spc_nr,
                spc_dsc,
                act_cat_nm,
                prs_sts_cd,
                prc_eff_dt,
                prc_dis_dt,
                prc_cur_cd,
                tot_amt,
                lbr_amt,
                pkt_nr,
                pkt_nm,
            )
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
            raise CustomException(
                "an error occurred while deleting the invoice history"
            )


class BillingReconService:
    def __init__(self, db_session):
        self.billing_recon_repository = BillingReconRepository(db_session)

    def process_billing_recon(self, data, filename=None):
        """
        Process billing reconciliation data and store it in the database.

        Args:
            data: The billing reconciliation data to process
            filename: Optional filename for tracking purposes

        Returns:
            bool: True if processing was successful
        """
        try:

            billing_data = self._prepare_billing_data(data)
            self.billing_recon_repository.insert_packeg_billing_recon(
                billing_data, filename
            )
            print("Successfully processed billing reconciliation data")

            return True

        except Exception as e:
            print(f"Error processing billing reconciliation data: {e}")
            raise CustomException(
                "An error occurred while processing billing reconciliation data"
            )

    def _prepare_billing_data(self, data):
        """
        Transform input data to the format expected by the repository.

        Args:
            data: Raw input data

        Returns:
            list: Formatted data ready for database insertion
        """
        return data

    def delete_billing_recon(self, id):
        """
        Delete a billing reconciliation record.

        Args:
            id: The ID of the record to delete

        Returns:
            dict: Message indicating success
        """
        try:
            return self.billing_recon_repository.delete_billing_recon(id)
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error deleting billing reconciliation: {e}")
            raise CustomException(
                "An error occurred while deleting the billing reconciliation"
            )

    def get_by_id(self, id):
        """
        Get a billing reconciliation record by ID.

        Args:
            id: The ID of the record to retrieve

        Returns:
            BillingRecon: The billing reconciliation record
        """
        try:
            return self.billing_recon_repository.get_by_id(id)
        except Exception as e:
            print(f"Error retrieving billing reconciliation: {e}")
            raise CustomException(
                "An error occurred while retrieving the billing reconciliation"
            )

    def get_by_flight_no(self, flight_no):
        """
        Get billing reconciliation records by flight number.

        Args:
            flight_no: The flight number to search for

        Returns:
            list: List of BillingRecon records
        """
        try:
            return self.billing_recon_repository.get_by_flight_no(flight_no)
        except Exception as e:
            print(
                "Error retrieving billing "
                f"reconciliation by flight number: {e}"
            )
            raise CustomException(
                "An error occurred while "
                "retrieving billing reconciliation records"
            )

    def search_billing_recon(
        self,
        flight_no=None,
        facility=None,
        item_code=None
    ):

        try:
            query = (
                self.billing_recon_repository.session.query(BillingRecon)
                .filter(BillingRecon.Excluido is False)
            )

            if flight_no:
                query = query.filter(BillingRecon.FltNo == flight_no)

            if facility:
                query = query.filter(
                    BillingRecon.Facility.ilike(f"%{facility}%")
                )

            if item_code:
                query = query.filter(BillingRecon.Itemcode == item_code)

            return query.all()
        except Exception as e:
            print(f"Error searching billing reconciliation records: {e}")
            raise CustomException(
                "An error occurred while "
                "searching billing reconciliation records"
            )


class ErpInvoiceReportService:
    def __init__(self, db_session):
        self.erp_invoice_repository = ErpInvoiceReportRepository(db_session)

    def process_erp_invoice(self, data, filename=None):
        """
        Process ERP invoice report data and store it in the database.

        Args:
            data: The ERP invoice data to process
            filename: Optional filename for tracking purposes

        Returns:
            bool: True if processing was successful
        """
        try:
            # Assuming data is already in the correct format for processing
            # If data needs transformation, add that logic here
            invoice_data = self._prepare_invoice_data(data)
            self.erp_invoice_repository.insert_packeg_erp_invoice(
                invoice_data, filename
            )

            print("Successfully processed ERP invoice data")

            return True

        except Exception as e:
            print(f"Error processing ERP invoice data: {e}")
            raise CustomException(
                "An error occurred while processing ERP invoice data"
            )

    def _prepare_invoice_data(self, data):
        """
        Transform input data to the format expected by the repository.

        Args:
            data: Raw input data
        Returns:
            list: Formatted data ready for database insertion
        """
        return data

    def delete_erp_invoice(self, id):
        """
        Delete an ERP invoice report record.

        Args:
            id: The ID of the record to delete

        Returns:
            dict: Message indicating success
        """
        try:
            return self.erp_invoice_repository.delete_erp_invoice(id)
        except CustomException as e:
            raise e

        except Exception as e:
            print(f"Error deleting ERP invoice: {e}")
            raise CustomException(
                "An error occurred while deleting the ERP invoice"
            )

    def get_by_id(self, id):
        """
        Get an ERP invoice report record by ID.

        Args:
            id: The ID of the record to retrieve

        Returns:
            ErpInvoiceReport: The ERP invoice report record
        """
        try:
            return self.erp_invoice_repository.get_by_id(id)
        except Exception as e:
            print(f"Error retrieving ERP invoice: {e}")
            raise CustomException(
                "An error occurred while retrieving the ERP invoice"
            )

    def get_by_flight_no(self, flight_no):
        """
        Get ERP invoice report records by flight number.

        Args:
            flight_no: The flight number to search for

        Returns:
            list: List of ErpInvoiceReport records
        """
        try:
            return self.erp_invoice_repository.get_by_flight_no(flight_no)
        except Exception as e:
            print(f"Error retrieving ERP invoice by flight number: {e}")
            raise CustomException(
                "An error occurred while retrieving ERP invoice records"
            )

    def search_erp_invoice(
        self,
        flight_no=None,
        supplier=None,
        service_code=None
    ):
        """
        Search for ERP invoice reports based on various criteria.

        Args:
            flight_no: Optional flight number to search for
            supplier: Optional supplier name to search for
            service_code: Optional service code to search for

        Returns:
            list: List of matching ErpInvoiceReport records
        """
        try:
            query = (
                self.erp_invoice_repository.session.query(ErpInvoiceReport)
                .filter(ErpInvoiceReport.Excluido is False)
            )

            if flight_no:
                query = query.filter(ErpInvoiceReport.FlightNo == flight_no)

            if supplier:
                query = query.filter(
                    ErpInvoiceReport.Supplier.ilike(f"%{supplier}%")
                )

            if service_code:
                query = query.filter(
                    ErpInvoiceReport.ServiceCode == service_code
                )

            return query.all()

        except Exception as e:
            print(f"Error searching ERP invoices: {e}")
            raise CustomException(
                "An error occurred while searching ERP invoice records"
            )
