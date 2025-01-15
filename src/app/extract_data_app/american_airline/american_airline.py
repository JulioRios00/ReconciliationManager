from flask import Flask, request, jsonify
from common.s3 import get_file_body_by_key
from services.css_service import FlightService
from flask_authorize import Authorize
from common.conexao_banco import get_session
import io
from services.airline_service import extract_data

app = Flask(__name__)

def main(event, context):
    file, size = get_file_body_by_key(event['key'], event['bucket'])
    file_content = file.read()
    pdf_bytes = io.BytesIO(file_content)
    with get_session() as session:
        flight_service = FlightService(session)
        flight_service.process_pdf_and_store(pdf_bytes, event['bucket'], event['key'])
    return jsonify({"message": "File processed and flights uploaded successfully"}), 201

    