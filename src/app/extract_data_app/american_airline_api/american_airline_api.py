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

# Application-Specific Services
from services.css_service import FlightService, PriceReportService

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

#Table priceReport
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

# @app.route(ROUTE_PREFIX + '/search/price_report/<string:id>', methods=['GET'])
# @authorize.in_group('admin')
# @ValidateParameters(flask_parameter_validation_handler)
# def search_price_report(id: str = Route(min_str_length=30, max_str_length=60), facility: str = Json(), organization: str = Json(), pulled_date: str = Json(), run_date: str = Json(), fac_org: str = Json(), spc_nr: str = Json(), spc_dsc: str = Json(), 
#                 act_cat_nm: str = Json(), prs_sts_cd: str = Json(), prc_eff_dt: str = Json(), prc_dis_dt: str = Json(), prc_cur_cd: str = Json(), tot_amt: str = Json(), lbr_amt: str = Json(), 
#                 pkt_nr: str = Json(), pkt_nm: str = Json()):
#     with get_session() as session:
#         try:
#             result = PriceReportService(session).check_item(facility=facility, organization=organization, pulled_date=pulled_date, run_date=run_date, fac_org=fac_org, spc_nr=spc_nr, spc_dsc=spc_dsc, 
#                 act_cat_nm=act_cat_nm, prs_sts_cd=prs_sts_cd, prc_eff_dt=prc_eff_dt, prc_dis_dt=prc_dis_dt, prc_cur_cd=prc_cur_cd, tot_amt=tot_amt, lbr_amt=lbr_amt, 
#                 pkt_nr=pkt_nr, pkt_nm=pkt_nm)
#             if not result:
#                 return jsonify({"message": "No records found"}), 404
#             print('-------------------------------------------------------')
#             print(result)
#             print('-------------------------------------------------------')
#             # Serialize the result (handle both single and multiple records)
#             if isinstance(result, list):
#                 return jsonify([item.serialize() for item in result]), 200
#             else:
#                 return jsonify(result.serialize()), 200

#         except CustomException as e:
#             return jsonify({'error': str(e)}), 400
#         except Exception as e:
#             return jsonify({'error': 'Internal server error'}), 500
        
def add_body(event):
    if 'body' not in event:
        event['body'] = '{}'
        headers = event['headers']
        headers['content-type'] = 'application/json'
    return event


def main(event, context):
    event = add_body(event)
    return serverless_wsgi.handle_request(app, event, context)


