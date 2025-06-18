# Standard Library Imports
import io
import os
import json
import logging

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
from services.reconciliation_service import ReconciliationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
authorize = Authorize(current_user=get_current_user, app=app)

ROUTE_PREFIX = '/invoice-reports'


# Get all Air Company Invoice Reports
@app.route(ROUTE_PREFIX + '/air-company', methods=['GET'])
@authorize.in_group('admin')
def get_all_air_company_reports():
    """
    Get all data from AirCompanyInvoiceReport table with pagination
    """    
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
    except (ValueError, TypeError) as e:
        logger.error(f"Parameter conversion error: {e}")
        return jsonify({'error': 'limit and offset must be valid integers'}), 400
        
    if limit < 1 or limit > 100:
        return jsonify({'error': 'limit must be between 1 and 100'}), 400
    if offset < 0:
        return jsonify({'error': 'offset must be 0 or greater'}), 400

    try:
        with get_session() as session:
            reconciliation_service = ReconciliationService(session)
            result = reconciliation_service.get_all_air_company_reports(
                limit=limit,
                offset=offset
            )
            
            if isinstance(result, tuple):
                error_data, status_code = result
                logger.error(f"Service returned error: {error_data}, status: {status_code}")
                return jsonify(error_data), status_code

            return jsonify(result), 200

    except CustomException as e:
        logger.error(f"CustomException: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected exception: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


# Get all Catering Invoice Reports
@app.route(ROUTE_PREFIX + '/catering', methods=['GET'])
@authorize.in_group('admin')
def get_all_catering_reports():
    """
    Get all data from CateringInvoiceReport table with pagination
    """
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
    except (ValueError, TypeError) as e:
        logger.error(f"Parameter conversion error: {e}")
        return jsonify({'error': 'limit and offset must be valid integers'}), 400

    if limit < 1 or limit > 100:
        return jsonify({'error': 'limit must be between 1 and 100'}), 400
    if offset < 0:
        return jsonify({'error': 'offset must be 0 or greater'}), 400

    try:
        with get_session() as session:
            reconciliation_service = ReconciliationService(session)

            result = reconciliation_service.get_all_catering_reports(
                limit=limit,
                offset=offset
            )

            if isinstance(result, tuple):
                error_data, status_code = result
                logger.error(f"Catering service returned error: {error_data}, status: {status_code}")
                return jsonify(error_data), status_code

            return jsonify(result), 200

    except CustomException as e:
        logger.error(f"CustomException in catering: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected exception in catering: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


def add_body(event):
    if 'body' not in event:
        event['body'] = '{}'
        headers = event['headers']
        headers['content-type'] = 'application/json'
    return event


def main(event, context):
    logger.info("Lambda main function started")
    logger.info(f"Event: {json.dumps(event, default=str)}")
    event = add_body(event)
    return serverless_wsgi.handle_request(app, event, context)