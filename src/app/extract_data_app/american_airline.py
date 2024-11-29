from common.s3 import get_file_body_by_key
from services.american_airline_service import extract_data
import io


def main(event, context):
    key = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']

    file, size = get_file_body_by_key(key, bucket)
    file_content = file.read()

    if not file_content:  # Check if the file is empty
        print("Error: The PDF file is empty.")
        return

    pdf_bytes = io.BytesIO(file_content)
    extract_data(pdf_bytes, bucket)
    print("===== Done =====")
