import os
import sys
import json
from common.conexao_banco import get_session
from services.reconciliation_service import ReconciliationService

project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main(event, context):
    """Lambda handler for populating reconciliation table"""
    try:
        # Get query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        force_populate = query_params.get('force_populate', '').lower() == 'true'
        
        with get_session() as session:
            reconciliation_service = ReconciliationService(session)
            
            # Check if table already has data (unless force_populate is true)
            if not force_populate:
                try:
                    existing_count = reconciliation_service.reconciliation_repository.get_count()
                    if existing_count > 0:
                        return {
                            "statusCode": 200,
                            "body": json.dumps({
                                "message": f"Reconciliation table already contains {existing_count} records. Use force_populate=true to repopulate.",
                                "existing_records": existing_count,
                                "populated": False
                            }),
                            "headers": {
                                "Content-Type": "application/json",
                                "Access-Control-Allow-Origin": "*",
                                "Access-Control-Allow-Credentials": True
                            }
                        }
                except Exception as e:
                    print(f"Warning: Could not check existing records count: {str(e)}")
                    # Continue with population if we can't check
            
            print("Starting reconciliation table population...")
            result = reconciliation_service.populate_reconciliation_table()
            
            if result.get("success"):
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "message": result.get("message"),
                        "summary": result.get("summary"),
                        "populated": True,
                        "timestamp": context.aws_request_id if context else None
                    }),
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Credentials": True
                    }
                }
            else:
                return {
                    "statusCode": 500,
                    "body": json.dumps({
                        "message": result.get("message"),
                        "error": "Failed to populate reconciliation table",
                        "populated": False
                    }),
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Credentials": True
                    }
                }
                
    except Exception as e:
        print(f"Error in populate_reconciliation: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Internal server error",
                "error": str(e),
                "populated": False
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            }
        }


if __name__ == "__main__":
    # For local testing
    test_event = {
        "queryStringParameters": {
            "force_populate": "true"
        }
    }
    
    class MockContext:
        aws_request_id = "local-test-123"
    
    result = main(test_event, MockContext())
    print(json.dumps(result, indent=2))