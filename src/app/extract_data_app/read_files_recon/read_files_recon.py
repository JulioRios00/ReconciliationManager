import json
import os
from io import StringIO
from common.s3 import get_file_body_by_key, list_objects
from services.ccs_file_readers_service import FileReadersService
from common.conexao_banco import get_session

READER_FUNCTIONS = {
    'billing_inflair_recon_report': 'billing_inflair_recon_report',
    'billing_promeus_invoice_report': 'billing_promeus_invoice_report',
    'pricing_read_inflair': 'pricing_read_inflair',
    'pricing_read_promeus_with_flight_classes':
        'pricing_read_promeus_with_flight_classes'
}

PREFIX_TO_PROCESSOR = {
    'public/airline_files/Airline Billing History/':
        'billing_inflair_recon_report',
    'public/airline_files/GCG Invoice History/':
        'billing_promeus_invoice_report',
}


def main(event, context):
    print("event object", event)

    if 'detail' in event:
        key = event['detail']['object']['key']
        bucket = event['detail']['bucket']['name']
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Unsupported event format'
            })
        }

    processor_function_name = None
    for prefix, processor in PREFIX_TO_PROCESSOR.items():
        if key.startswith(prefix):
            processor_function_name = processor
            break

    if not processor_function_name:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': f'No processor found for file: {key}'
            })
        }

    reader_method_name = READER_FUNCTIONS.get(processor_function_name)
    if not reader_method_name:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': f'Unknown reader function: {processor_function_name}'
            })
        }

    print(f"Using processor: {processor_function_name},"
          f" method: {reader_method_name}"
          )

    analised_files, size = get_file_body_by_key(
        "public/airline_files/analised_files_list.json",
        bucket
    )

    analyzed_files_json = json.loads(analised_files.read())
    print(f'Analyzed files: {analyzed_files_json}')

    sub_path = key.replace('public/airline_files/', '', 1)
    parts = sub_path.split('/', 1)

    if len(parts) == 2:
        folder_name, file_name = parts

        folder_mapping = {
            'Airline Billing History': 'Airline Billing History',
            'GCG Invoice History': 'GCG Invoice History',
            'Airline Price Report': 'Airline Price Report',
            'GCG Price Report': 'GCG Price Report'
        }

        mapped_folder = folder_mapping.get(folder_name)
        if mapped_folder and mapped_folder in analyzed_files_json:
            if file_name in analyzed_files_json[mapped_folder]:
                print(f"File {file_name} already analyzed.")
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'File already analyzed',
                        'file': file_name
                    })
                }

    file, size = get_file_body_by_key(key, bucket)
    file_content = file.read()
    print(f'File size: {size} bytes')

    temp_dir = '/tmp'
    temp_file_path = os.path.join(temp_dir, f"temp_{os.path.basename(key)}")

    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_content)

    try:
        with get_session() as session:
            file_reader_service = FileReadersService(session)
            reader_method = getattr(file_reader_service, reader_method_name)
            data = reader_method(temp_file_path)

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
