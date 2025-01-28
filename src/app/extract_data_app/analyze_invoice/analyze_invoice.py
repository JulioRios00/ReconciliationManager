from flask import Flask, request, jsonify
from common.s3 import get_file_body_by_key
from services.css_service import InvoiceService
from common.conexao_banco import get_session
import os
import io

def main(event, context):
    # key = event['Records'][0]['s3']['object']['key']
    # bucket = event['Records'][0]['s3']['bucket']['name']
    # file, size = get_file_body_by_key(key, bucket)
    file, size = get_file_body_by_key(event['key'], event['bucket'])
    file_content = file.read()

    if not file_content:
        print("Error: The file file is empty.")
 
    with get_session() as session:
        invoices_service = InvoiceService(session)
        invoices_service.process_invoice(file_content, event['file_name'])
