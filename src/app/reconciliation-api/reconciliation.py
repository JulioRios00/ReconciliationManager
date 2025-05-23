import os
import sys
import json
import logging
import traceback

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'))
logger = logging.getLogger()

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.conexao_banco import get_session
from services.reconciliation_service import ReconciliationService


def main(event, context):
    """
    Lambda handler for retrieving reconciliation data with pagination
    """
    logger.info("Received request for reconciliation data")

    try:
        # Paginação do retorno do endpoint
        query_params = event.get('queryStringParameters', {}) or {}
        limit = int(query_params.get('limit', 100))
        offset = int(query_params.get('offset', 0))

        with get_session() as session:
            result = (
                ReconciliationService(session)
                .get_paginated_reconciliation_data(limit, offset)
            )

        if (isinstance(result, tuple) and len(result) == 2
                and isinstance(result[1], int)):
            return {
                "statusCode": result[1],
                "body": json.dumps(result[0]),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True
                }
            }

        return {
            "statusCode": 200,
            "body": json.dumps(result),
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
