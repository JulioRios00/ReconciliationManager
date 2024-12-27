import json
import csv
from io import StringIO

def price_report_data(input_bytes):
    data = {}
    header_data = {}
    price_data = [] 

    try:
        # Decode bytes to string
        decoded_data = input_bytes.decode('utf-8')
        lines = decoded_data.splitlines()  # Split into lines

        # Extract meta-data (first 5 lines)
        for i in range(5):
            header_data[f"Line {i + 1}"] = lines[i].strip()

        # Extract headers and table data
        csv_content = '\n'.join(lines[6:])  # Skip lines 0-5
        csv_reader = csv.DictReader(StringIO(csv_content))

        # Convert CSV rows to dictionaries
        for row in csv_reader:
            price_data.append(row)

        # Combine meta information and table data
        data["Header Data"] = header_data
        data["Table Data"] = price_data

    except Exception as e:
        print(f"An error occurred: {e}")
    
    return header_data, price_data
    

