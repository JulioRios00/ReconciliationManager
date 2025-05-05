from flask import Flask, request, jsonify
from common.s3 import get_file_body_by_key
from services.ccs_service import PriceReportService
from common.conexao_banco import get_session
import os
import io

def main(event, context):    
    file, size = get_file_body_by_key(event['key'], event['bucket'])
    file_content = file.read()

    if not file_content:
        print("Error: The file file is empty.")

    with get_session() as session:
        price_report_service = PriceReportService(session)
        price_report_service.process_price_report(file_content)
