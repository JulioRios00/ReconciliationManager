from flask import Flask, request, jsonify
from common.s3 import get_file_body_by_key
from services.css_service import FlightService
from common.conexao_banco import get_session
import os
import io

def main(event, context):
    file, size = get_file_body_by_key(event['key'], event['bucket'])
    file_content = file.read()

    if not file_content:
        print("Error: The file file is empty.")

    pdf_bytes = io.BytesIO(file_content)
    with get_session() as session:
        flight_service = FlightService(session)
        flight_service.process_pdf_and_store(pdf_bytes, bucket, event['key'])
