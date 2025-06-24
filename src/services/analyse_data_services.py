import pandas as pd
import time
import datetime
from repositories.ccs_repository import ReconciliationRepository

# Application-Specific Services
from services.reconciliation_service import ReconciliationService

from common.conexao_banco import get_session
from common.custom_exception import CustomException
from flask import jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyseDataServices:
    def __init__(self):
        pass

    def compare_billing_invoice(self):
        start_time = time.time()
        """
        Compare billing invoice data with the database and Google Sheets.
        """
        print("Starting compare_billing_invoice function")

        try:
            with get_session() as session:
                reconciliation_repository = ReconciliationRepository(session)
                
                reports = reconciliation_repository.get_flight_class_mapping()
                flight_map = pd.DataFrame([{
                    key: value
                    for key, value in report.__dict__.items()
                    if not key.startswith("_")
                } for report in reports])

                print(len(reports))
                print(flight_map)



                reports = reconciliation_repository.get_all_catering_reports()
                billing = pd.DataFrame([{
                    key: value
                    for key, value in report.__dict__.items()
                    if not key.startswith("_")
                } for report in reports])


                reports = reconciliation_repository.get_all_air_company_reports()
                invoice = pd.DataFrame([{
                    key: value
                    for key, value in report.__dict__.items()
                    if not key.startswith("_")
                } for report in reports])


                billing_columns = ['FltDate', 'FltNo', 'Class', 'Itemcode', 'Qty', 'UnitPrice', 'TotalAmount']
                billing = billing[billing_columns]
                # Ensure consistent column naming
                billing = billing.rename(columns={'FltDate': 'Billing_FlightDate', 
                                                'FltNo': 'Billing_FlightNo', 
                                                'Class': 'Billing_Class', 
                                                'Itemcode': 'Billing_Itemcode', 
                                                'Qty': 'Billing_Qty', 
                                                'UnitPrice': 'Billing_UnitPrice', 
                                                'TotalAmount': 'Billing_TotalAmount'})
                billing['Billing_FlightDate'] = pd.to_datetime(billing['Billing_FlightDate'], format='%d/%m/%y')

                invoice_columns = ['FlightDate', 'FlightNo', 'Class', 'ServiceCode', 'Qty', 'UnitPrice', 'SubTotal']
                invoice = invoice[invoice_columns]
                # Ensure consistent column naming
                invoice = invoice.rename(columns={'FlightDate': 'Invoice_FlightDate', 
                                                'FlightNo': 'Invoice_FlightNo', 
                                                'Class':  'Invoice_Class', 
                                                'ServiceCode':  'Invoice_ServiceCode', 
                                                'Qty':  'Invoice_Qty', 
                                                'UnitPrice':  'Invoice_UnitPrice',
                                                'SubTotal':  'Invoice_SubTotal'})

                invoice['Invoice_FlightNo'] = invoice['Invoice_FlightNo'].str.strip()
                invoice['Invoice_FlightDate'] = pd.to_datetime(invoice['Invoice_FlightDate'], errors='coerce')

                # # Merge the billing with flight_map
                # # Merge dataframes on ALBillCode
                # merged_df = pd.merge(billing, flight_map, on=['Billing_FlightNo'], how='left')

                # # Eliminate rows where column 'Invoice_FlightNo' is None
                # merged_df = merged_df.dropna(subset=['Invoice_FlightNo'])


                end_time = time.time()
                exec_time = datetime.timedelta(seconds=(end_time - start_time))
                print(f'\n --- O tempo de excursão para a previsão: {exec_time} (h:m:s) ---')
                print('=====================')  

                return '200'

        except CustomException as e:
            print(f"CustomException: {e}")
            logger.error(f"CustomException: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            print(f"Unexpected exception: {e}")
            logger.error(f"Unexpected exception: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500




