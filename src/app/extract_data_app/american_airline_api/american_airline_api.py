from flask import Flask, request, jsonify
from common.s3 import get_file_body_by_key
from common.error_handling import all_exception_handler, flask_parameter_validation_handler
from services.css_service import FlightService, PriceReportService
from flask_authorize import Authorize
from common.conexao_banco import get_session
from common.authorization import get_current_user
from flask_parameter_validation import ValidateParameters, Query, Json, Route
import io
import os
import json
import serverless_wsgi

app = Flask(__name__)
authorize = Authorize(current_user=get_current_user, app=app)

ROUTE_PREFIX = '/flights'

@app.route(ROUTE_PREFIX + '/upload/american_airline', methods=['POST'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def upload_flight_data(file_name: str = Json() ):
    try:
        bucket = os.getenv('MTW_BUCKET_NAME')
        key = 'public/airline_pdf/'+file_name
        file, size = get_file_body_by_key(key, bucket)
        file_content = file.read()
        pdf_bytes = io.BytesIO(file_content)

        with get_session() as session:
            flight_service = FlightService(session)
            flight_service.process_pdf_and_store(pdf_bytes, bucket, file_name)
        return jsonify({"message": "File processed and flights uploaded successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route(ROUTE_PREFIX + '/upload/price_report', methods=['POST'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def upload_price_report_data(file_name: str = Json() ):
    try:
        bucket = os.getenv('MTW_BUCKET_NAME')
        key = 'public/price_report/'+file_name
        file, size = get_file_body_by_key(key, bucket)
        file_content = file.read()

        if not file_content:  # Check if the file is empty
            print("Error: The file file is empty.")

        with get_session() as session:
            price_report_service = PriceReportService(session)
            price_report_service.process_price_report(file_content)
        return jsonify({"message": "File processed and price report data uploaded successfully"}), 201    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def is_api_gateway_event(event):
    if 'httpMethod' in event.keys():
        print(1, 'httpMethod' in event.keys())
        return True    
    else:
        print(2, 'http' in event)
        return 'http' in event

def main(event, context):
    print('=============================')
    print(f'{event=}')
    print('=============================')

    if is_api_gateway_event(event):
        print("This is an API Gateway request")
        with app.app_context():
            return serverless_wsgi.handle_request(app, event, context)
    else:
        print("This is a direct Lambda invocation")
        api_input = json.loads(event['body'])
        print(f'{api_input=}')



