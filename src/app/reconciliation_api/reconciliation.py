import os
import sys
import json
import logging
import traceback
from decimal import Decimal
from datetime import datetime
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


def validate_date_format(date_str):
    """
    Validate date format YYYY-MM-DD

    Args:
        date_str: Date string to validate

    Returns:
        bool: True if valid format or None/empty, False otherwise
    """
    if not date_str:
        return True
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def main(event, context):
    """
    Lambda handler for retrieving reconciliation
    data with pagination and filtering
    """
    logger.info("Received request for reconciliation data")
    try:
        query_params = event.get('queryStringParameters', {}) or {}
        limit = int(query_params.get('limit', 100))
        offset = int(query_params.get('offset', 0))
        filter_type = query_params.get('filter_type', 'all')
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        valid_filter_types = [
            'all',
            'discrepancies',
            'quantity_difference',
            'price_difference',
            'air_only',
            'cat_only'
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

        if not validate_date_format(start_date):
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Invalid start_date format. Use YYYY-MM-DD"
                }),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True
                }
            }

        if not validate_date_format(end_date):
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Invalid end_date format. Use YYYY-MM-DD"
                }),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True
                }
            }

        if start_date and end_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                if start_dt > end_dt:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({
                            "message": "start_date cannot be"
                            " greater than end_date"
                        }),
                        "headers": {
                            "Content-Type": "application/json",
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Credentials": True
                        }
                    }
            except ValueError as e:
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": f"Date parsing error: {str(e)}"
                    }),
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Credentials": True
                    }
                }

        if limit <= 0 or limit > 1000:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Limit must be between 1 and 1000"
                }),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True
                }
            }

        if offset < 0:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Offset must be non-negative"
                }),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True
                }
            }

        logger.info(f"Request parameters - limit: {limit}, offset: {offset}, "
                    f"filter_type: {filter_type}, start_date: {start_date}, "
                    f"end_date: {end_date}")

        with get_session() as session:
            result = (
                ReconciliationService(session)
                .get_paginated_reconciliation_data(
                    limit=limit,
                    offset=offset,
                    filter_type=filter_type,
                    start_date=start_date,
                    end_date=end_date
                )
            )
        if (isinstance(result, tuple) and len(result) == 2
                and isinstance(result[1], int)):
            return {
                "statusCode": result[1],
                "body": json.dumps(result[0], cls=DecimalEncoder),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True
                }
            }

        return {
            "statusCode": 200,
            "body": json.dumps(result, cls=DecimalEncoder),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            }
        }

    except ValueError as ve:
        logger.error(
            f"Validation error in reconciliation data handler: {str(ve)}"
            )
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid input parameters",
                "error": str(ve)
            }),
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
