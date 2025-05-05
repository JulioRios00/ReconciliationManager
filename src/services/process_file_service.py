import pandas as pd
import json
from datetime import datetime


def read_flight_invoice_report(file_path: str) -> pd.DataFrame:
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

    return df


def flight_invoice_report_to_json(file_path: str) -> str:
    """
    Reads a flight invoice report Excel file
    and returns the data as a JSON string.

    Args:
        file_path: Path to the Excel file

    Returns:
        JSON string representation of the flight invoice data
    """
    df = read_flight_invoice_report(file_path)

    processed_data = []

    for _, row in df.iterrows():
        if pd.isna(row["Number"]) or "-" in str(row["Number"]):
            continue

        flight_date = row["Date"]
        invoice_date = row["Date.1"]

        if isinstance(flight_date, datetime):
            flight_date = flight_date.strftime("%d/%m/%Y")

        if isinstance(invoice_date, datetime):
            invoice_date = invoice_date.strftime("%d/%m/%Y")

        record = {
            "Flight Number": str(row["Number"]).strip(),
            "Flight Date": flight_date,
            "Invoice Number": str(row["Number.1"]).strip(),
            "Invoice Date": invoice_date,
            "First Class Passengers": (
                int(row["F"]) if pd.notna(row["F"]) else 0
            ),
            "Business Class Passengers": (
                int(row["J"]) if pd.notna(row["J"]) else 0
            ),
            "Economy Class Passengers": (
                int(row["Y"]) if pd.notna(row["Y"]) else 0
            ),
            "Goods Value": (
                float(row["Goods Value"])
                if pd.notna(row["Goods Value"])
                else 0.0
            ),
            "Galley Service": (
                float(row["Galley Serv"])
                if pd.notna(row["Galley Serv"])
                else 0.0
            ),
            "Total Amount": (
                float(row["Total"]) 
                if pd.notna(row["Total"])
                else 0.0),
            "Statement": (
                str(row["Statement"]).strip()
                if pd.notna(row["Statement"])
                else ""
            ),
            "Period": (
                str(row["Period"]).strip()
                if pd.notna(row["Period"])
                else ""
            ),
            "Currency": str(row["Cd"]).strip() if pd.notna(row["Cd"]) else "",
        }

        processed_data.append(record)

    return json.dumps(processed_data, ensure_ascii=False, indent=2)


def read_clean_invoice_report(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path, header=0)

    expected_columns = {"SUPPLIER", "FLIGHT DATE", "FLIGHT NO.", "DEP", "ARR"}
    if not expected_columns.issubset(df.columns):
        raise ValueError("Please share the correct file.")

    df.dropna(how="all", inplace=True)

    df.dropna(axis=1, how="all", inplace=True)

    df.reset_index(drop=True, inplace=True)

    return df


def clean_invoice_report_to_json(file_path: str) -> str:
    """
    Reads a clean invoice report Excel file
    and returns the data as a JSON string.

    Args:
        file_path: Path to the Excel file

    Returns:
        JSON string representation of the clean invoice data
    """
    df = read_clean_invoice_report(file_path)

    processed_data = []

    for _, row in df.iterrows():
        flight_date = row.get("FLIGHT DATE")
        invoice_date = row.get("INVOICE DATE")
        paid_date = row.get("PAID DATE")

        if isinstance(flight_date, datetime):
            flight_date = flight_date.strftime("%Y-%m-%d")

        if isinstance(invoice_date, datetime):
            invoice_date = invoice_date.strftime("%Y-%m-%d")

        if isinstance(paid_date, datetime):
            paid_date = paid_date.strftime("%Y-%m-%d")

        record = {
            "Supplier": str(row.get("SUPPLIER", "")).strip(),
            "Flight Date": flight_date,
            "Flight Number": str(row.get("FLIGHT NO.", "")).strip(),
            "Departure": str(row.get("DEP", "")).strip(),
            "Arrival": str(row.get("ARR", "")).strip(),
            "Class": str(row.get("CLASS", "")).strip(),
            "Invoiced Passengers": (
                int(row.get("INVOICED PAX", 0))
                if pd.notna(row.get("INVOICED PAX"))
                else 0
            ),
            "Service Code": str(row.get("SERVICE CODE", "")).strip(),
            "Supplier Code": str(row.get("SUPPLIER CODE", "")).strip(),
            "Service Description": (
                str(row.get("SERVICE DESCRIPTION", "")).strip()
                if pd.notna(row.get("SERVICE DESCRIPTION"))
                else ""
            ),
            "Aircraft": str(row.get("AIRCRAFT", "")).strip(),
            "Quantity": (
                int(row.get("QTY", 0))
                if pd.notna(row.get("QTY"))
                else 0
                ),
            "Unit Price": (
                float(row.get("UNIT PRICE", 0.0))
                if pd.notna(row.get("UNIT PRICE"))
                else 0.0
            ),
            "Subtotal": (
                float(row.get("SUBTOTAL", 0.0))
                if pd.notna(row.get("SUBTOTAL"))
                else 0.0
            ),
            "Tax": (
                float(row.get("TAX", 0.0))
                if pd.notna(row.get("TAX"))
                else 0.0
                ),
            "Total Including Tax": (
                float(row.get("TOTAL INC TAX", 0.0))
                if pd.notna(row.get("TOTAL INC TAX"))
                else 0.0
            ),
            "Currency": str(row.get("CURRENCY", "")).strip(),
            "Item Status": str(row.get("ITEM STATUS", "")).strip(),
            "Invoice Status": str(row.get("INVOICE STATUS", "")).strip(),
            "Invoice Date": invoice_date,
            "Paid Date": paid_date,
        }

        processed_data.append(record)

    return json.dumps(processed_data, ensure_ascii=False, indent=2)


# Create a function that send the data to the database
def send_to_database(data: str):
    """
    Placeholder function to send data to the database.
    This function should be implemented according to the database being used.
    """
    # Implement database connection and data insertion logic here
    pass
