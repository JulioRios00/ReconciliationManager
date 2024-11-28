import PyPDF2
import time
import datetime
import re
import json
from datetime import datetime as dt
import io 
from common.s3 import upload_file
import fitz

def read_pdf_page_by_page(pdf_file):
    """
    Reads the content of a PDF file page by page.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        if len(pdf_reader.pages) == 0:
            return "Error: The PDF file is empty."
        return [page.extract_text() for page in pdf_reader.pages]
    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"


def detect_bold_text(page):
    bold_texts = []
    for block in page.get_text("dict")["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    if "bold" in span["font"].lower() and span["text"].strip():
                        bold_texts.append(span["text"])
    return bold_texts


def process_page_content(page_content):
    flight_details_match = re.search(r"(AA-AMERICAN AIRLINES.*)", page_content, re.DOTALL | re.IGNORECASE)
    flight_details = flight_details_match.group(0).strip() if flight_details_match else None
    if flight_details and "FlightDetails" in flight_details:
        class_details = page_content.replace(flight_details, "").strip()
        return flight_details, class_details
    else:
        return None, None


def extract_dates_from_bold_text(bold_text):
    """
    Extracts dates from bold text based on month and year.
    """
    month_year_match = re.search(
        r'(January|February|March|April|May|June|July|August|September|October|November|December), (\d{4})',
        ' '.join(bold_text))
    if not month_year_match:
        return []
    month, year = month_year_match.group(1), int(month_year_match.group(2))
    days = [text for text in bold_text if re.match(r'^\d+$', text)]
    full_dates = []
    for day in days:
        try:
            date_str = f"{day} {month} {year}"
            date_obj = dt.strptime(date_str, "%d %B %Y")
            full_dates.append(date_obj.strftime("%Y-%m-%d"))
        except ValueError:
            continue
    return full_dates


def extract_and_organize_dates(bold_texts):
    """
    Organizes extracted dates into a structured format.
    """
    organized_dates = []
    current_month_year = None
    for text in bold_texts:
        if "," in text:
            current_month_year = text.strip()
        elif text.isdigit() and current_month_year:
            day = int(text)
            month, year = current_month_year.split(", ")
            month_number = {
                "January": "01", "February": "02", "March": "03",
                "April": "04", "May": "05", "June": "06",
                "July": "07", "August": "08", "September": "09",
                "October": "10", "November": "11", "December": "12"
            }.get(month, "00")
            formatted_date = f"{day:02d}/{month_number}/{year}"
            organized_dates.append(formatted_date)
    return organized_dates


def extract_flight_data(page_content, organized_dates, last_data=None):
    """
    Extracts structured flight information from the given page content.
    This function now uses a dictionary to preserve previous values if they are not overwritten.

    Args:
        page_content (str): The text content of the page.
        organized_dates (list): The list of dates in dd/mm/yyyy format.
        last_data (dict): The last known set of flight data to keep values if they aren’t overwritten.

    Returns:
        dict: A dictionary containing extracted flight information.
    """
    # Initialize flight_data with last_data if provided, to persist previous values
    flight_data = last_data or {}

    # Set 'Empresa Aérea' with a fixed value for all pages
    flight_data["Empresa Aérea"] = "AA-AMERICAN AIRLINES"

    # Extract the 'periodo'
    periodo_match = re.search(r"Effv\s*-\s*Disc:\s*(\d{4}-\d{2}-\d{2}\s*-\s*\d{4}-\d{2}-\d{2})", page_content)
    if periodo_match:
        flight_data["periodo"] = periodo_match.group(1)

    # Extract the 'unidade'
    unidade_match = re.search(r"Facility:\s*(\w+)", page_content)
    if unidade_match:
        flight_data["unidade"] = unidade_match.group(1)

    # Extract the 'ciclo'
    ciclo_match = re.search(r"Cycle:\s*(\d+)", page_content)
    if ciclo_match:
        flight_data["ciclo"] = ciclo_match.group(1)
    
    # Extract the 'datas'
    if organized_dates:
        flight_data["datas"] = ", ".join(organized_dates)

    # Extract the serving flight number (Vr Voo)
    vr_voo_match = re.search(r"\(Serve\)\s*Flt Nbr:\s*(\d+)", page_content)
    if vr_voo_match:
        flight_data["Vr Voo"] = vr_voo_match.group(1)

    # Extract data from "Dpt Sta" to "Arr Sta"
    # Extract the second occurrence of data between "Dpt Sta" and "Arr Sta" for origem
    origem_matches = re.findall(r"Dpt Sta:(.*?)Arr Sta:", page_content, re.DOTALL)
    if len(origem_matches) > 1:
        flight_data["origem"] = origem_matches[1].strip()  # Second occurrence

    # Extract the second occurrence of data between "Arr Sta" and "Dpt Tm" for destino
    destino_matches = re.findall(r"Arr Sta:(.*?)Dpt Tm:", page_content, re.DOTALL)
    if len(destino_matches) > 1:
        flight_data["destino"] = destino_matches[1].strip()  # Second occurrence

    # Extract the second occurrence of 'hora partida' (departure time)
    partida_matches = re.findall(r"Dpt Tm:\s*(\d{2}:\d{2})", page_content)
    if len(partida_matches) > 1:
        flight_data["hora partida"] = partida_matches[1]

    # Extract 'hora chegada' (arrival time) for the serving flight
    chegada_match = re.search(r"Arr Tm:\s*(\d{2}:\d{2})", page_content)
    if chegada_match:
        flight_data["hora chegada"] = chegada_match.group(1)

    # Extract 'aeronave' (equipment type)
    aeronave_match = re.search(r"Equip:\s*(\w+)", page_content)
    if aeronave_match:
        flight_data["aeronave"] = aeronave_match.group(1)

    return flight_data


def parse_service_data(page_content, last_class=None):
    """
    Parses service data from the page content.
    """
    data = {}
    current_class = last_class
    current_packet = None
    lines = page_content.splitlines()

    for line in lines:
        line = line.strip()
        if line.startswith("Class of Service:"):
            current_class = line.split(":")[1].strip()
            data[current_class] = {}
        elif line.startswith("Packet :"):
            packet_match = re.match(r"Packet : (\d+)\s*-\s*(.+?)\s+(\w{5})", line)
            if packet_match:
                packet_number, packet_text, destino = packet_match.groups()
                current_packet = f"{packet_number} - {packet_text}"
                if current_class:
                    data.setdefault(current_class, {})[current_packet] = {
                        "destino": destino,
                        "items": []
                    }
        elif re.match(r"IT\d+", line):
            item_match = re.match(
                r"(IT\d+)\s+(.+?)\s+(V-\d+|\d+%|0%)\s*,?\s*(S-\d+)?\s*([PMTN]?)\s*(\d+)?", line
            )
            if item_match:
                item = {
                    "Item Code": item_match.group(1),
                    "Descrição": item_match.group(2).strip(),
                    "Provision_1": item_match.group(3) or "",
                    "Provision_2": item_match.group(4) or "",
                    "type": item_match.group(5) or "",
                    "Svc": item_match.group(6) or "0"
                }
                if current_packet and current_class:
                    data[current_class][current_packet]["items"].append(item)

    return data, current_class or last_class


def extract_data(pdf_file, bucket):
    """
    Processes the PDF file, extracts data similar to process_pdf_page_by_page, and uploads extracted data as a JSON file to S3.
    """    
    start_time = time.time()
    print("Start time:", start_time)

    pages = read_pdf_page_by_page(pdf_file)
    if isinstance(pages, str):
        print(pages)
        return

    # Use PyMuPDF to open the PDF for more advanced processing
    pdf_document = fitz.open(stream=pdf_file, filetype="pdf")
    result_data = {}
    last_class = None

    for page_num, page_content in enumerate(pages, start=1):
        print(f"=== Processing Page {page_num} ===")
        page_data = {}

        # Process flight details and class details
        flight_details, class_details = process_page_content(page_content)
        if flight_details:
            # Use PyMuPDF to extract bold text from the page
            page = pdf_document.load_page(page_num - 1)
            bold_texts = detect_bold_text(page)
            extracted_dates = extract_and_organize_dates(bold_texts)
            final_data = extract_flight_data(flight_details, extracted_dates)
            page_data["final_data"] = final_data  # Store final data for the current page

            if class_details:
                # Parse service data using class details
                service_data, last_class = parse_service_data(class_details, last_class)
                page_data["service_data"] = service_data  # Store service data for the current page
        else:
            print("\nNo relevant flight details found on this page. Skipping.")
            continue

        # Add page data to the result data dictionary with page number as key
        result_data[f"Page {page_num}"] = page_data

    # Convert the result data to JSON
    body = json.dumps(result_data, indent=6)

    # Define S3 file key and upload
    file_key = "public/test_pdf/results.json"
    upload_file(file_key, bucket, body)

    print(f"Data successfully uploaded to S3 at {file_key}")

    end_time = time.time()
    exec_time = datetime.timedelta(seconds=(end_time - start_time))
    print(f'\n--- Execution Time: {exec_time} ---')
