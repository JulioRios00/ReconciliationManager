import pandas as pd
import json
import os
from collections import defaultdict
import numpy as np
from typing import List, Dict, Any
from datetime import datetime, date
from repositories.ccs_repository import (
    CateringInvoiceRepository,
    AirCompanyInvoiceRepository,
)
from models.schema_ccs import CateringInvoiceReport, AirCompanyInvoiceReport


class FileReadersService:
    def __init__(self, db_session):
        self.catering_invoice_repository = CateringInvoiceRepository(
            db_session
            )
        self.air_company_invoice_repository = AirCompanyInvoiceRepository(
            db_session
            )
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
            self.air_company_invoice_repository.insert_air_company_invoice(
                data
            )
            print(f"Successfully inserted {len(data)} air company invoice records into the database")
        except Exception as e:
            print(f"Error inserting ERP invoice data: {e}")

        # save_json(data, "billing_promeus.json")

        # return data

    def billing_inflair_recon_report(
        self,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """
        Reads the Inflair Airline Billing Recon Report (CSV or Excel)
        and returns a list of records.

        Parameters
        ----------
        file_path : str
            Path to the CSV or Excel file

        Returns
        -------
        List[Dict[str, Any]]
            List of records from the file
        """
        extension = os.path.splitext(file_path)[1].lower()
        MAX_HEADER_SEARCH_LINES = 15
        DEFAULT_HEADER_FALLBACK = 8
        skip_rows = 0
        df = None

        if extension == ".csv":
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = []
                for i in range(MAX_HEADER_SEARCH_LINES):
                    try:
                        line = f.readline()
                        if not line:
                            break
                        lines.append(line.strip())
                    except (EOFError, IOError):
                        break

                for i, line in enumerate(lines):
                    if line.startswith("Facility"):
                        skip_rows = i
                        break
                else:
                    skip_rows = DEFAULT_HEADER_FALLBACK

            df = pd.read_csv(file_path, skiprows=skip_rows)

        elif extension in [".xls", ".xlsx"]:
            engine = "openpyxl" if extension == ".xlsx" else "xlrd"

            try:
                df_temp = pd.read_excel(
                    file_path, nrows=15,
                    engine=engine,
                    header=None
                )

                for idx, row in df_temp.iterrows():
                    if str(row[0]).strip() == "Facility":
                        skip_rows = idx
                        break
                else:
                    skip_rows = DEFAULT_HEADER_FALLBACK
                
            except Exception as e:
                print(f"Error reading header: {e}")
                skip_rows = DEFAULT_HEADER_FALLBACK

            df = pd.read_excel(file_path, skiprows=skip_rows, engine=engine)

        else:
            raise ValueError("Unsupported file format. "
                             "Only .csv, .xls, and .xlsx are supported.")

        if len(df) > 2:
            df = df.dropna(how='all')

            if len(df) > 2:
                df = df.iloc[:-2]

        df.columns = [
            col.strip() if isinstance(col, str) else col for col in df.columns
        ]

        print("Detected columns:", df.columns.tolist())

        column_mapping = {
            "Facility": "facility",
            "Flt Date": "flt_date",
            "Flt No.": "flt_no",
            "Flt Inv": "flt_inv",
            "Class": "class_",
            "Item Group": "item_group",
            "Item code": "itemcode",
            "Item Desc": "item_desc",
            "A/L Bill Code": "al_bill_code",
            "A/L Bill Desc": "al_bill_desc",
            "Bill Catg": "bill_catg",
            "Unit": "unit",
            "PAX": "pax",
            "Qty": "qty",
            "Unit Price": "unit_price",
            "Total Amount": "total_amount",
            "FltDate": "flt_date",
            "FltNo": "flt_no",
            "Fl Inv": "flt_inv",
            "Ite Group": "item_group",
            "Ite code": "itemcode",
            "Ite Desc": "item_desc",
            "AlBillCode": "al_bill_code",
            "AlBillDesc": "al_bill_desc",
            "BillCatg": "bill_catg",
            "Pax": "pax",
            "UnitPrice": "unit_price",
            "TotalAmount": "total_amount",
        }

        df = df.rename(columns=column_mapping)

        if "flt_no" in df.columns:
            df["flt_no"] = df["flt_no"].apply(
                lambda x: (f"0{x}" 
                           if isinstance(x, (int, float)) and x < 100 else str(x)
                           )
            )

        if "flt_date" in df.columns:
            df["flt_date"] = df["flt_date"].apply(format_date)

        for col in ["pax", "qty", "unit_price", "total_amount"]:
            if col in df.columns:
                df[col] = df[col].astype(str)

        df = df.replace({np.nan: None})

        df = df[df['facility'].notna()]

        data = df.to_dict(orient="records")
        
        if data:
            print("First record:", data[0])
            print(f"Total records found: {len(data)}")
        else:
            print("No data records found")

        try:
            if data:
                model_instances = [
                    CateringInvoiceReport(**item) for item in data
                ]
                self.catering_invoice_repository.bulk_insert(model_instances)
                print(
                    f"Successfully inserted {len(data)} "
                    "billing reconciliation records into the database"
                    )
            else:
                print("No data to insert")
        except Exception as e:
            print(f"Error inserting billing reconciliation data: {e}")
            import traceback
            print(traceback.format_exc())

        return data

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
