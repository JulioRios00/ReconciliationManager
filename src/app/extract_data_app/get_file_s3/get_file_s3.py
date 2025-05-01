import json
import boto3
import os
import sys
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.ccs_file_readers_db_service import (
    save_billing_inflair_to_db,
    save_billing_promeus_to_db,
    save_pricing_inflair_to_db,
    save_pricing_promeus_to_db
)

# Map of function names to actual functions
PROCESSOR_FUNCTIONS = {
    'save_billing_inflair_to_db': save_billing_inflair_to_db,
    'save_billing_promeus_to_db': save_billing_promeus_to_db,
    'save_pricing_inflair_to_db': save_pricing_inflair_to_db,
    'save_pricing_promeus_to_db': save_pricing_promeus_to_db
}


def debug_environment():
    debug_info = {
        "python_version": sys.version,
        "sys_path": sys.path,
        "current_dir": os.getcwd(),
        "dir_contents": os.listdir('.'),
        "lambda_task_root": os.environ.get('LAMBDA_TASK_ROOT', 'Not set'),
        "lambda_runtime_dir": os.environ.get('LAMBDA_RUNTIME_DIR', 'Not set'),
        "env_vars": dict(os.environ)
    }
    
    try:
        import pandas
        debug_info["pandas_version"] = pandas.__version__
        debug_info["pandas_path"] = pandas.__path__
    except ImportError as e:
        debug_info["pandas_error"] = str(e)
    
    return debug_info


def main(event, context):
    # Parse the incoming event
    body = json.loads(event['body'])
    bucket_name = body['bucketName']
    object_key = body['objectKey']
    processor_function_name = body['processorFunction']

    # Get the processor function
    processor_function = PROCESSOR_FUNCTIONS.get(processor_function_name)
    if not processor_function:
        return {
            'statusCode': 400,
            'body': json.dumps(
                {'error': f'Unknown processor function: '
                          f'{processor_function_name}'}
                )
        }

    # Create a temporary file to store the S3 object
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name

    try:

        s3_client = boto3.client('s3')
        s3_client.download_file(bucket_name, object_key, temp_path)

        db_url = os.environ['DATABASE_URL']
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        result = processor_function(temp_path, db)

        os.unlink(temp_path)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'File processed successfully',
                'records_processed': len(result) if result else 0
            })
        }
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(temp_path):
            os.unlink(temp_path)

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
