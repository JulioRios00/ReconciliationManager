# Standard Library Imports
import io
import os
import json

# Third-Party Library Imports
from flask import Flask, request, jsonify
from flask_authorize import Authorize
from flask_parameter_validation import ValidateParameters, Query, Json, Route
import serverless_wsgi

# Application-Specific Common Utilities
from common.s3 import get_file_body_by_key
from common.error_handling import all_exception_handler, flask_parameter_validation_handler
from common.conexao_banco import get_session
from common.authorization import get_current_user
from common.custom_exception import CustomException
from common.lambda_boto import invoke_lambda_async

# Application-Specific Services
from services.css_service import FlightService, PriceReportService

app = Flask(__name__)
authorize = Authorize(current_user=get_current_user, app=app)

ROUTE_PREFIX = '/flights'

@app.route(ROUTE_PREFIX + '/upload/airline', methods=['POST'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def upload_flight_data(file_name: str = Json() ):
    try:
        key = 'public/airline_files/TP_006/'+file_name
        payload = {'key':key}
        invoke_lambda_async('arn:aws:lambda:us-east-1:018061303185:function:serverless-ccs-dev-american_airline', payload)
        return jsonify({"message": "File processed and flights uploaded successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Table priceReport
@app.route(ROUTE_PREFIX + '/upload/price_report', methods=['POST'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def upload_price_report_data(file_name: str = Json() ):
    print('file_name____', file_name)
    try:
        key = 'public/airline_files/TP_100/'+file_name
        payload = {'key':key, 'file_name':file_name}
        invoke_lambda_async('arn:aws:lambda:us-east-1:018061303185:function:serverless-ccs-dev-american_airline', payload)
        return jsonify({"message": "File processed and flights uploaded successfully"}), 201    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route(ROUTE_PREFIX + '/delete/price_report/<string:id>', methods=['DELETE'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def delete_price_report(id: str = Route(min_str_length=30, max_str_length=60)):
    with get_session() as session:
        try:
            result = PriceReportService(session).delete_price_report(id)
            return jsonify(result), 204
        except CustomException as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

@app.route(ROUTE_PREFIX + '/search/price_report/<string:id>', methods=['GET'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def search_price_report(id: str = Route(min_str_length=30, max_str_length=60), spc_dsc: str = Json()):
    with get_session() as session:
        try:
            result = PriceReportService(session).search_price_report(id=id, spc_dsc=spc_dsc)
            if not result:
                return jsonify({"message": "No records found"}), 404
            
            # Serialize the result (handle both single and multiple records)
            if isinstance(result, list):
                return jsonify([item.serialize() for item in result]), 200
            else:
                return jsonify(result.serialize()), 200

        except CustomException as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500


def add_body(event):
    if 'body' not in event:
        event['body'] = '{}'
        headers = event['headers']
        headers['content-type'] = 'application/json'
    return event


def main(event, context):
    event = add_body(event)
    return serverless_wsgi.handle_request(app, event, context)
