import json
import boto3
import os
import io
import sys
import tempfile
from io import StringIO
from common.s3 import get_file_body_by_key
from services.ccs_file_readers_service import (
    billing_inflair_invoice_report,
    billing_promeus_invoice_report,
    pricing_read_inflair,
    pricing_read_promeus_with_flight_classes
)

READER_FUNCTIONS = {
    'save_billing_inflair_to_db': billing_inflair_invoice_report,
    'save_billing_promeus_to_db': billing_promeus_invoice_report,
    'save_pricing_inflair_to_db': pricing_read_inflair,
    'save_pricing_promeus_to_db': pricing_read_promeus_with_flight_classes
}


def main(event, context):

    key = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']
    processor_function_name = (
        event['Records'][0]['s3']['object']['processorFunction']
    )

    reader_function = READER_FUNCTIONS.get(processor_function_name)
    if not reader_function:
        return {
            'statusCode': 400,
            'body': json.dumps(
                {'error': f'Unknown reader function: '
                          f'{processor_function_name}'}
                )
        }

    file, size = get_file_body_by_key(key, bucket)
    file_content = file.read()

    temp_dir = '/tmp'
    temp_file_path = os.path.join(temp_dir, f"temp_{os.path.basename(key)}")

    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_content)

    try:
        data = reader_function(temp_file_path)

        os.unlink(temp_file_path)

        if isinstance(data, list):
            serialized_data = data
            records_count = len(data)
        elif isinstance(data, dict):
            serialized_data = {
                class_name: items for class_name,
                items in data.items()
            }
            records_count = sum(len(items) for items in data.values())
        else:
            serialized_data = str(data)
            records_count = 0

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'File read successfully',
                'data': serialized_data,
                'records_count': records_count
            }, default=str)
        }
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
