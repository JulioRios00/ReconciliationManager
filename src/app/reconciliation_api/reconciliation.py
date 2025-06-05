import os
import sys
import json
import logging
import traceback
from decimal import Decimal
from common.conexao_banco import get_session
from services.reconciliation_service import ReconciliationService

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'))
logger = logging.getLogger()

project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def main(event, context):
    """
    Lambda handler for retrieving reconciliation data with pagination and date filtering
    """
    logger.info("Received request for reconciliation data")
    logger.info(f"Event: {json.dumps(event)}")
    
    try:
        query_params = event.get('queryStringParameters', {}) or {}
        logger.info(f"Query parameters: {query_params}")
        
        limit = int(query_params.get('limit', 100))
        offset = int(query_params.get('offset', 0))
        filter_type = query_params.get('filter_type', 'all')
        start_date = query_params.get('start_date')  # Add this
        end_date = query_params.get('end_date')      # Add this

        logger.info(f"Parsed parameters: limit={limit}, offset={offset}, filter_type={filter_type}")
        logger.info(f"Date range: start_date={start_date}, end_date={end_date}")

        valid_filter_types = [
            'all',
            'discrepancies',
            'air_only',
            'cat_only',
            'quantity_difference',
            'price_difference'
        ]
        if filter_type not in valid_filter_types:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": (f"Invalid filter_type. Must be one of: "
                                f"{', '.join(valid_filter_types)}")
                }),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True
                }
            }

        with get_session() as session:
            # Pass the date parameters to the service
            result = (
                ReconciliationService(session)
                .get_paginated_reconciliation_data(
                    limit=limit, 
                    offset=offset, 
                    filter_type=filter_type,
                    start_date=start_date,  # Add this
                    end_date=end_date       # Add this
                )
            )
            
        logger.info(f"Service returned: {type(result)}")
        
        if (isinstance(result, tuple) and len(result) == 2
                and isinstance(result[1], int)):
            logger.error(f"Service returned error: {result}")
            return {
                "statusCode": result[1],
                "body": json.dumps(result[0], cls=DecimalEncoder),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True
                }
            }

        logger.info(f"Returning successful response with {len(result.get('data', []))} records")
        return {
            "statusCode": 200,
            "body": json.dumps(result, cls=DecimalEncoder),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            }
        }
    except Exception as e:
        logger.error(f"Error in reconciliation data handler: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Internal server error",
                "error": str(e)
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            }
        }
