import pandas as pd
import json
from collections import defaultdict
import numpy as np
from typing import List, Dict, Any
from datetime import datetime, date
from repositories.ccs_repository import (
    BillingReconRepository,
    ErpInvoiceReportRepository,
)
from models.schema_ccs import BillingRecon


class FileReadersService:
    def __init__(self, db_session):
        self.billing_recon_repository = BillingReconRepository(db_session)
        self.erp_invoice_repository = ErpInvoiceReportRepository(db_session)
        self.session = db_session

    def billing_inflair_invoice_report(
        self,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """
        This method reads the billing inflair file and returns an array
        of objects and a json file (will be commented in the code)
        """
        df = pd.read_excel(file_path, skiprows=12, header=None)

        df.columns = [
            "Number",
            "Date",
            "Date.1",
            "Number.1",
            "F",
            "J",
            "Y",
            "Goods Value",
            "Galley Serv",
            "Total",
            "Statement",
            "Period",
            "Cd",
        ]

        footer_patterns = [
            "----",
            "====",
            "End of Invoice",
            "Accounts - Flight",
            "TOTAL",
        ]

        mask = (
            ~df["Number"].astype(str).str
            .contains("|".join(footer_patterns), na=False)
        )
        df = df[mask]

        for col in df.select_dtypes(include=["datetime64"]).columns:
            df[col] = df[col].apply(format_date)

        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].apply(
                lambda x: x.strip() if isinstance(x, str) else x
            )

        df = df.replace({np.nan: None})

        data = df.to_dict(orient="records")

        # save_json(data, "billing_inflair.json")

        return data

    # gcg
    def billing_promeus_invoice_report(
        self,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """
        This method reads the billing promeus file and returns an
        array of objects and a json file (will be commented in the code)
        """
        df = pd.read_excel(file_path, header=0)

        expected_columns = {
            "SUPPLIER",
            "FLIGHT DATE",
            "FLIGHT NO.",
            "DEP",
            "ARR"
        }
        if not expected_columns.issubset(df.columns):
            raise ValueError("Please share the correct file.")

        df.dropna(how="all", inplace=True)
        df.dropna(axis=1, how="all", inplace=True)
        df.reset_index(drop=True, inplace=True)

        column_mapping = {
            "SUPPLIER": "Supplier",
            "FLIGHT DATE": "FlightDate",
            "FLIGHT NO.": "FlightNo",
            "DEP": "Dep",
            "ARR": "Arr",
            "CLASS": "Class",
            "INVOICED PAX": "InvoicedPax",
            "SERVICE CODE": "ServiceCode",
            "SUPPLIER CODE": "SupplierCode",
            "SERVICE DESCRIPTION": "ServiceDescription",
            "AIRCRAFT": "Aircraft",
            "QTY": "Qty",
            "UNIT PRICE": "UnitPrice",
            "SUBTOTAL": "SubTotal",
            "TAX": "Tax",
            "TOTAL INC TAX": "TotalIncTax",
            "CURRENCY": "Currency",
            "ITEM STATUS": "ItemStatus",
            "INVOICE STATUS": "InvoiceStatus",
            "INVOICE DATE": "InvoiceDate",
            "PAID DATE": "PaidDate",
        }

        df = df.rename(columns=column_mapping)

        if "FlightNo" in df.columns:
            df["FlightNoRed"] = df["FlightNo"].apply(
                lambda x: (
                    "".join(char for char in str(x) if char.isdigit())
                    if x else None
                )
            )

        if "FlightDate" in df.columns:
            try:
                df["FlightDate"] = pd.to_datetime(df["FlightDate"]).dt.strftime("%Y-%m-%d")
                print(f"Flight date conversion successful: {df['FlightDate']}")
            except Exception as e:
                print(f"Error converting FlightDate: {e}")
                print(f"Original FlightDate values: {df['FlightDate'].head()}")

        for col in df.select_dtypes(include=["datetime64"]).columns:
            df[col] = df[col].apply(format_date)

        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].apply(
                lambda x: x.strip() if isinstance(x, str) else x
            )

        if "InvoicedPax" in df.columns:
            df["InvoicedPax"] = df["InvoicedPax"].astype(str)

        df = df.replace({np.nan: None})

        data = df.to_dict(orient="records")

        try:
            self.erp_invoice_repository.insert_package_erp_invoice(data)
            print(
                f"Successfully inserted {len(data)} \
                ERP invoice records into the database"
            )
        except Exception as e:
            print(f"Error inserting ERP invoice data: {e}")

        # save_json(data, "billing_promeus.json")

        # return data

    def pricing_read_promeus_with_flight_classes(
        self, file_path: str
    ) -> List[Dict[str, Any]]:
        df = pd.read_excel(
            file_path,
            sheet_name="Price History Report",
            engine="openpyxl",
            header=None
        )

        records = []
        current_class = None
        header_processed = False

        for index, row in df.iterrows():
            first_col = row[0]
            service_code = row[2]
            description = row[3]
            currency = row[4]
            price = row[5]

            if (
                pd.isna(service_code)
                and pd.isna(description)
                and pd.isna(currency)
                and pd.isna(price)
                and isinstance(first_col, str)
            ):
                current_class = first_col.strip()
                continue
            if (
                not header_processed
                and isinstance(service_code, str)
                and service_code == "Service Code"
            ):
                header_processed = True
                continue
            if (
                not pd.isna(service_code)
                and not pd.isna(description)
                and not pd.isna(price)
            ):
                records.append(
                    {
                        "class": current_class,
                        "facility": first_col,
                        "service_code": service_code,
                        "description": description,
                        "currency": currency,
                        "price": price,
                    }
                )

        # save_json(records, "pricing_promeus.json")
        return records

    def pricing_read_inflair(self, file_path: str) -> List[Dict[str, Any]]:
        df = pd.read_excel(file_path, skiprows=8)

        df.columns = [
            "id",
            "airline_code",
            "item_code",
            "start_date",
            "end_date",
            "cost_center",
            "unit",
            "price",
            "currency",
            "created_date",
            "created_time",
            "created_by",
            "type_of_change",
            "statement_period",
        ]

        df = df[df["item_code"].notna()]
        df = df[~df["id"].astype(str).str.match(r"^-+$", na=False)]

        df["price"] = pd.to_numeric(df["price"], errors="coerce").round(3)
        df["start_date"] = df["start_date"].apply(format_date)
        df["end_date"] = df["end_date"].apply(format_date)
        df["created_date"] = df["created_date"].apply(format_date)

        df = df.replace({np.nan: None})

        result = df.to_dict(orient="records")
        # save_json(result, "pricing_inflair.json")
        return result

	#Airline billing history
    def billing_inflair_recon_report(
        self,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """
        This method reads the Inflair Airline Billing Recon Report CSV
        file and returns an array of objects and saves a JSON file.

        Parameters
        ----------
        file_path : str
            Path to the CSV file

        Returns
        -------
        List[Dict[str, Any]]
            List of records from the CSV file
        """
        df = pd.read_csv(file_path)
		## corrigir problema de leitura do arquivo
        if len(df) > 2:
            df = df.iloc[:-2]

        df.columns = [
            col.strip() if isinstance(col, str) else col for col in df.columns
        ]

        column_mapping = {
            "Facility": "Facility",
            "FltDate": "FltDate",
            "FltNo": "FltNo",
            "Fl Inv": "FltInv",
            "Class": "Class",
            "Ite Group": "ItemGroup",
            "Ite code": "Itemcode",
            "Ite Desc": "ItemDesc",
            "AlBillCode": "AlBillCode",
            "AlBillDesc": "AlBillDesc",
            "BillCatg": "BillCatg",
            "Unit": "Unit",
            "Pax": "Pax",
            "Qty": "Qty",
            "UnitPrice": "UnitPrice",
            "TotalAmount": "TotalAmount",
        }

        df = df.rename(columns=column_mapping)

        if "FltNo" in df.columns:
            df["FltNo"] = df["FltNo"].apply(
                lambda x: (f"0{x}" if isinstance(x, (int, float))
                           and x < 100 else x)
            )

        if "FltDate" in df.columns:
            df["FltDate"] = df["FltDate"].apply(format_date)

        for col in ["Pax", "Qty", "UnitPrice", "TotalAmount"]:
            if col in df.columns:
                df[col] = df[col].astype(str)

        df = df.replace({np.nan: None})

        data = df.to_dict(orient="records")
        print("first record", data[0])

        try:
            # Convert dictionaries to model instances before bulk insert            
            model_instances = []
            for item in data:
                model_instance = BillingRecon()
                for key, value in item.items():
                    if hasattr(model_instance, key):
                        setattr(model_instance, key, value)
                model_instances.append(model_instance)

            self.billing_recon_repository.bulk_insert(model_instances)
            print(
                f"Successfully inserted {len(data)} \
                billing reconciliation records into the database"
            )
        except Exception as e:
            print(f"Error inserting billing reconciliation data: {e}")

        # Return the original data for the Lambda function
        return data


def format_date(date_value) -> date:
    """
    Converts a date value to datetime.date format 'YYYY-MM-DD'.
    Accepts formats: 'D/M/YYYY', 'D/M/YY', Timestamp and datetime.date objects.
    """
    if isinstance(date_value, pd.Timestamp):
        return date_value.date()
        
    if isinstance(date_value, date):
        return date_value
        
    if not date_value or not isinstance(date_value, str):
        return None

    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(date_value.strip(), fmt).date()
        except ValueError:
            continue

    print(f"Error formatting date: {date_value}")
    return None


def group_data_by_class(data):
    grouped_data = defaultdict(list)

    for item in data:
        class_name = item.get("class")
        if (
            not class_name or
            "facility" not in item
            or item["facility"] == "Facility"
        ):
            continue

        item_copy = item.copy()
        item_copy.pop("class")
        grouped_data[class_name].append(item_copy)

    return dict(grouped_data)


def save_json(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
