from flask import Flask, request, jsonify
from common.s3 import get_file_body_by_key
from services.css_service import PriceReportService
from flask_authorize import Authorize
from common.conexao_banco import get_session
import io

app = Flask(__name__)

def main(event, context):
    key = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']

    file, size = get_file_body_by_key(key, bucket)
    file_content = file.read()
    # pdf_bytes = io.BytesIO(file_content)

    if not file_content:  # Check if the file is empty
        print("Error: The file file is empty.")
    try:
        with get_session() as session:
            price_report_service = PriceReportService(session)
            price_report_service.process_price_report(file_content)
        return jsonify({"message": "File processed and flights uploaded successfully"}), 201    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


