import pandas as pd
import json
from collections import defaultdict
import numpy as np
from typing import List, Dict, Any


def format_date(date_value) -> str:
    """Format dates in YYYY-MM-DD"""
    if pd.isna(date_value):
        return None
    try:
        return pd.to_datetime(date_value).strftime("%Y-%m-%d")
    except Exception:
        return None


def group_data_by_class(data):
    grouped_data = defaultdict(list)

    for item in data:
        class_name = item.get("class")
        if (
            not class_name
            or "facility" not in item
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


def billing_inflair_invoice_report(file_path: str) -> List[Dict[str, Any]]:
    """
    This method reads the billing inflair file and returns an array of objects
    and a json file (will be commented in the code)
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
        "----", "====", "End of Invoice", "Accounts - Flight", "TOTAL"
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


def billing_promeus_invoice_report(file_path: str) -> pd.DataFrame:
    """
    This method reads the billing promeus file and returns an
    array of objects and a json file (will be commented in the code)
    """
    df = pd.read_excel(file_path, header=0)

    expected_columns = {"SUPPLIER", "FLIGHT DATE", "FLIGHT NO.", "DEP", "ARR"}
    if not expected_columns.issubset(df.columns):
        raise ValueError("Please share the correct file.")

    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)
    df.reset_index(drop=True, inplace=True)

    for col in df.select_dtypes(include=["datetime64"]).columns:
        df[col] = df[col].apply(format_date)

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

    df = df.replace({np.nan: None})

    data = df.to_dict(orient="records")

    # save_json(data, "billing_promeus.json")

    return data


def pricing_read_inflair(file_path: str) -> List[Dict[str, Any]]:
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
        "statement_period"
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


def pricing_read_promeus_with_flight_classes(file_path: str) -> List[Dict[str, Any]]:
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
            not header_processed and
            isinstance(service_code, str) and
                service_code == "Service Code"):
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

    # No longer grouping by class
    # save_json(records, "pricing_promeus.json")
    return records


def billing_inflair_recon_report(file_path: str) -> List[Dict[str, Any]]:
    """
    This method reads the Inflair Airline Billing Recon Report CSV file and returns
    an array of objects and saves a JSON file.

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

    df.columns = (
        [col.strip() if isinstance(col, str) else col for col in df.columns]
    )

    for col in df.select_dtypes(include=["datetime64"]).columns:
        df[col] = df[col].apply(format_date)

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    df = df.replace({np.nan: None})

    data = df.to_dict(orient="records")

    save_json(data, "billing_inflair_recon.json")

    return data
