import pandas as pd
import numpy as np
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

from repositories.ccs_repository import BillingInvoiceTotalDifferenceRepository
from models.schema_ccs import BillingInvoiceTotalDifference


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyseDataServices:
    def __init__(self):
        pass
    

    def convert_to_df(self, reports):
        df = pd.DataFrame(
                    [
                        {key: value
                            for key, value in report.__dict__.items()
                            if not key.startswith("_")
                        }
                        for report in reports
                    ]
                )
        return df
    
    def add_to_database(self, df, AnalysedField):
                        # Agrupar por data (usando a data de faturamento, por exemplo)
                df_grouped = df.groupby('Billing_FlightDate').agg({
                    'Billing_TotalAmount': 'sum',
                    'Invoice_SubTotal': 'sum'
                }).reset_index()
    
                for i in range(len(df_grouped)):
                    row = df_grouped.iloc[i]
                    record = BillingInvoiceTotalDifference(
                        AnalysedField=AnalysedField,
                        AnalysedItem='Billing Total Amount',
                        FlightDate=row['Billing_FlightDate'].date(),
                        TotalAmount=row['Billing_TotalAmount']
                    )
                    self.billing_invoice_total_difference_repository.add_record(record)
                    record = BillingInvoiceTotalDifference(
                        AnalysedField=AnalysedField,
                        AnalysedItem='Invoice SubTotal',
                        FlightDate=row['Billing_FlightDate'].date(),
                        TotalAmount=row['Invoice_SubTotal']
                    )
                    self.billing_invoice_total_difference_repository.add_record(record)


    def compare_billing_invoice(self):

        start_time = time.time()
        """
        Compare billing invoice data with the database and Google Sheets.
        """
        print("Starting compare_billing_invoice function")

        try:
            with get_session() as session:
                reconciliation_repository = ReconciliationRepository(session)

                # ==== Get all flight numbe mapping reports ====
                reports = reconciliation_repository.get_all_flight_number_reports()
                flight_map = self.convert_to_df(reports)
                cols = ['CateringFlightNumber', 'AirCompanyFlightNumber']
                flight_map = flight_map[cols].rename(columns={'CateringFlightNumber': 'Billing_FlightNo', 'AirCompanyFlightNumber': 'Invoice_FlightNo'})
                flight_map = flight_map[~flight_map['Invoice_FlightNo'].isin(['Charter'])]
                print(f'{len(flight_map)=}')

                # ==== Get all flight class mapping reports ====
                reports = reconciliation_repository.get_all_flight_class_reports()
                class_map = self.convert_to_df(reports)
                cols = ["ItemCode", "ALBillCode"]
                class_map = class_map[cols].rename(columns={"ItemCode": "Billing_Itemcode","ALBillCode": "Invoice_ServiceCode",})
                print(f'{len(class_map)=}')

                # ==== Get BillingRecon ====
                reports = reconciliation_repository.get_all_catering_reports()
                billing = self.convert_to_df(reports)

                # Identify duplicated rows
                duplicates = billing[billing.duplicated()]
                print(f'Duplicated rows in invoice: {len(duplicates)}')

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
                billing['Billing_TotalAmount'] = billing['Billing_TotalAmount'].astype(float)

                #  ==== Get ErpInvoiceReport  ==== 
                reports = reconciliation_repository.get_all_air_company_reports()
                invoice = self.convert_to_df(reports)
                # Identify duplicated rows
                duplicates = invoice[invoice.duplicated()]
                print(f'Duplicated rows in invoice: {len(duplicates)}')

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
                print(f'{len(invoice)=}')

                # ==== Merge the billing with flight_map ====
                # Merge dataframes on Billing_FlightNo
                merged_df = pd.merge(billing, flight_map, on=['Billing_FlightNo'], how='left')

                # Eliminate rows where column 'Invoice_FlightNo' is None
                merged_df = merged_df.dropna(subset=['Invoice_FlightNo'])

                # ==== Merge the merged_df with class_map ====
                # Merge dataframes on Billing_Itemcode
                merged_df = pd.merge(merged_df, class_map, on=['Billing_Itemcode'], how='left')


                # ==== Merge the merged_df with invoice ====
                # Merge dataframes on Invoice_FlightNo and Invoice_ServiceCode
                merged_df = pd.merge(merged_df, invoice, on=['Invoice_FlightNo', 'Invoice_ServiceCode'], how='left')

                df = merged_df[(merged_df['Billing_FlightDate'] == merged_df['Invoice_FlightDate'])]

                # ==== # clean the table ====
                self.billing_invoice_total_difference_repository = BillingInvoiceTotalDifferenceRepository(session)
                self.billing_invoice_total_difference_repository.delete_all()

                # ==== # Financial Analysis of Billing vs. Invoice Data ====
                print("The sum of the incove_TotalAmount", df['Invoice_SubTotal'].sum())
                print("The sum of the Billing_TotalAmount", df['Billing_TotalAmount'].sum())
                record = BillingInvoiceTotalDifference(
                    AnalysedField='TotalSum',
                    AnalysedItem='Invoice SubTotal',
                    FlightDate=datetime.datetime.now().date(),
                    TotalAmount=df['Invoice_SubTotal'].sum()
                )
                self.billing_invoice_total_difference_repository.add_record(record)

                record = BillingInvoiceTotalDifference(
                    AnalysedField='TotalSum',
                    AnalysedItem='Billing_TotalAmount',
                    FlightDate=datetime.datetime.now().date(),
                    TotalAmount=df['Billing TotalAmount'].sum()
                )
                self.billing_invoice_total_difference_repository.add_record(record)

                # Make a clean copy if df is a filtered version or slice
                df = df.copy()

                # ==== # Comparison of Billing and Invoice Amounts Over Time ====
                print("Comparison of Billing and Invoice Amounts Over Time ...")
                self.add_to_database(df, 'Comparison of Billing and Invoice Amounts Over Time')
                print("Comparison of Billing and Invoice Amounts Over Time completed.")

                # ==== # Comparison of Billing and Invoice Amounts Over Time by Billing Class ====
                print("Comparison of Billing and Invoice Amounts Over Time  by Billing Class ...")
                all_classes = df['Billing_Class'].unique()
                for class_name in all_classes:
                    class_df = df[df['Billing_Class'] == class_name]
                    print(f"Billing Class: {class_name}")
                    self.add_to_database(class_df, f'Billing Class: {class_name}')
                print("Comparison of Billing and Invoice Amounts Over Time  by Billing Class completed.")

                # ==== # Comparison of Billing and Invoice Amounts Over Time by Invoice Class ====
                print("Comparison of Billing and Invoice Amounts Over Time  by Invoice Class ...")
                all_classes = df['Invoice_Class'].unique()
                for class_name in all_classes:
                    class_df = df[df['Invoice_Class'] == class_name]
                    print(f"Invoice Class: {class_name}")
                    self.add_to_database(class_df, f'Billing Class: {class_name}')
                print("Comparison of Billing and Invoice Amounts Over Time  by Invoice Classes completed.")

                # ==== # Comparison of Billing and Invoice Amounts Over Time by Billing Itemcode ====
                print("Comparison of Billing and Invoice Amounts Over Time  by Billing Itemcode ...")
                top_10_by_total = (
                    df.groupby('Billing_Itemcode')['Billing_TotalAmount']
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                )

                for itemcode, total in top_10_by_total.items():
                    print(f"Itemcode: {itemcode}, Total Amount: {total:.2f}")
                    itemcode_df = df[df['Billing_Itemcode'] == itemcode]
                    self.add_to_database(class_df, f'Billing Itemcode: {itemcode}')
                print("Comparison of Billing and Invoice Amounts Over Time  by Billing Itemcode completed.")

             
                # ==== # Comparison of Billing and Invoice Amounts Over Time by Invoice Itemcode ====
                print("Comparison of Billing and Invoice Amounts Over Time  by Billing Itemcode ...")
                top_10_by_total = (
                    df.groupby('Invoice_ServiceCode')['Invoice_SubTotal']
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                )

                for itemcode, total in top_10_by_total.items():
                    print(f"Itemcode: {itemcode}, SubTotal: {total:.2f}")
                    itemcode_df = df[df['Invoice_ServiceCode'] == itemcode]
                    self.add_to_database(class_df, f'Invoice Itemcode: {itemcode}')
                print("Comparison of Billing and Invoice Amounts Over Time  by Billing Itemcode completed.")

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
