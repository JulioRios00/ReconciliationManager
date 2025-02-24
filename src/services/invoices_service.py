import csv
from io import StringIO

def analyze_invoices_data(input_bytes): 
    invoices_data = []

    try:
        # Decode bytes to string
        decoded_data = input_bytes.decode('utf-8')
        lines = decoded_data.splitlines()
        csv_content = '\n'.join(lines[1:])
        csv_reader = csv.DictReader(StringIO(csv_content))

        # Convert CSV rows to dictionaries
        for row in csv_reader:
            invoices_data.append(row)

    except Exception as e:
        print(f"An error occurred: {e}")
    
    return invoices_data