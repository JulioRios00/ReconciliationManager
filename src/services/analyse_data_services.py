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
import json
import boto3
import os


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

                # Get all flight numbe mapping reports
                reports = reconciliation_repository.get_all_flight_number_reports()
                flight_map = pd.DataFrame(
                    [
                        {
                            key: value
                            for key, value in report.__dict__.items()
                            if not key.startswith("_")
                        }
                        for report in reports
                    ]
                )
                cols = ["AirCompanyFlightNumber", "CateringFlightNumber"]
                flight_map = flight_map[cols].rename(
                    columns={
                        "CateringFlightNumber": "Billing_FlightNo",
                        "AirCompanyFlightNumber": "Invoice_FlightNo",
                    }
                )
                flight_map = flight_map[~flight_map["Invoice_FlightNo"].isin(["Charter"])]
                print(f'{len(flight_map)=}')

                # Get all flight class mapping reports
                reports = reconciliation_repository.get_all_flight_class_reports()
                class_map = pd.DataFrame(
                    [
                        {
                            key: value
                            for key, value in report.__dict__.items()
                            if not key.startswith("_")
                        }
                        for report in reports
                    ]
                )
                cols = ["ItemCode", "ALBillCode"]
                class_map = class_map[cols].rename(
                    columns={
                        "ItemCode": "Billing_Itemcode",
                        "ALBillCode": "Invoice_ServiceCode",
                    }
                )
                print(f'{len(class_map)=}')

                # Get BillingRecon
                reports = reconciliation_repository.get_all_catering_reports()
                billing = pd.DataFrame(
                    [
                        {
                            key: value
                            for key, value in report.__dict__.items()
                            if not key.startswith("_")
                        }
                        for report in reports
                    ]
                )
                print(f'{len(billing)=}')

                # Get ErpInvoiceReport
                reports = reconciliation_repository.get_all_air_company_reports()
                invoice = pd.DataFrame(
                    [
                        {
                            key: value
                            for key, value in report.__dict__.items()
                            if not key.startswith("_")
                        }
                        for report in reports
                    ]
                )
                print(f'{len(invoice)=}')

                billing_columns = [
                    "FltDate",
                    "FltNo",
                    "Class",
                    "Itemcode",
                    "Qty",
                    "UnitPrice",
                    "TotalAmount",
                ]
                billing = billing[billing_columns]
                # Ensure consistent column naming
                billing = billing.rename(
                    columns={
                        "FltDate": "Billing_FlightDate",
                        "FltNo": "Billing_FlightNo",
                        "Class": "Billing_Class",
                        "Itemcode": "Billing_Itemcode",
                        "Qty": "Billing_Qty",
                        "UnitPrice": "Billing_UnitPrice",
                        "TotalAmount": "Billing_TotalAmount",
                    }
                )
                billing['Billing_FlightDate'] = pd.to_datetime(billing['Billing_FlightDate'], format="%Y-%m-%d")

                invoice_columns = [
                    "FlightDate",
                    "FlightNo",
                    "Class",
                    "ServiceCode",
                    "Qty",
                    "UnitPrice",
                    "SubTotal",
                ]
                invoice = invoice[invoice_columns]
                # Ensure consistent column naming
                invoice = invoice.rename(
                    columns={
                        "FlightDate": "Invoice_FlightDate",
                        "FlightNo": "Invoice_FlightNo",
                        "Class": "Invoice_Class",
                        "ServiceCode": "Invoice_ServiceCode",
                        "Qty": "Invoice_Qty",
                        "UnitPrice": "Invoice_UnitPrice",
                        "SubTotal": "Invoice_SubTotal",
                    }
                )

                invoice["Invoice_FlightNo"] = invoice["Invoice_FlightNo"].str.strip()
                invoice["Invoice_FlightDate"] = pd.to_datetime(
                    invoice["Invoice_FlightDate"], errors="coerce"
                )

                # Merge dataframes on Billing_FlightNo
                merged_df = pd.merge(
                    billing, flight_map, on=["Billing_FlightNo"], how="left"
                )

                # Eliminate rows where column 'Invoice_FlightNo' is None
                merged_df = merged_df.dropna(subset=["Invoice_FlightNo"])

                # Merge dataframes on Billing_Itemcode
                merged_df = pd.merge(
                    merged_df, class_map, on=["Billing_Itemcode"], how="left"
                )

                # Merge dataframes on Billing_Itemcode
                merged_df = pd.merge(
                    merged_df,
                    invoice,
                    on=["Invoice_FlightNo", "Invoice_ServiceCode"],
                    how="left",
                )

                df = merged_df[
                    (merged_df["Billing_FlightDate"] == merged_df["Invoice_FlightDate"])
                ]
                df["Invoice_SubTotal"] = df["Invoice_SubTotal"].astype(float)
                df["Billing_TotalAmount"] = df["Billing_TotalAmount"].astype(float)

                print("The sum of the incove_TotalAmount", df["Invoice_SubTotal"].sum())
                print("The sum of the Billing_TotalAmount", df["Billing_TotalAmount"].sum())

                analyse_results = {'incove_TotalAmount': df["Invoice_SubTotal"].sum(),
                                   'Billing_TotalAmount': df["Billing_TotalAmount"].sum()}
                
                file_key = f'public/airline_analysis/analyse_results.json'                        
                s3 = boto3.client('s3')
                bucket_name = os.getenv("MTW_BUCKET_NAME")
                s3.put_object(
                    Bucket=bucket_name,
                    Key=file_key,
                    Body=json.dumps(analyse_results, default=str)
                )

                end_time = time.time()
                exec_time = datetime.timedelta(seconds=(end_time - start_time))
                print(
                    f"\n --- O tempo de excursão para a previsão: {exec_time} (h:m:s) ---"
                )
                print("=====================")

                return "200"

        except CustomException as e:
            print(f"CustomException: {e}")
            logger.error(f"CustomException: {e}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            print(f"Unexpected exception: {e}")
            logger.error(f"Unexpected exception: {e}", exc_info=True)
            return jsonify({"error": "Internal server error"}), 500
