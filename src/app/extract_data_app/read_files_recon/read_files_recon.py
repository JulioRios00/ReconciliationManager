import json
import os

from common.conexao_banco import get_session
from common.s3 import get_file_body_by_key
from services.ccs_file_readers_service import FileReadersService

READER_FUNCTIONS = {
    "billing_inflair_recon_report": "billing_inflair_recon_report",
    "billing_promeus_invoice_report": "billing_promeus_invoice_report",
    "pricing_read_inflair": "pricing_read_inflair",
    "pricing_read_promeus_with_flight_classes": "pricing_read_promeus_with_flight_classes",
    "read_flight_class_mapping": "read_flight_class_mapping",
    "read_flight_number_mapping": "read_flight_number_mapping",
}

PREFIX_TO_PROCESSOR = {
    "public/airline_files/Airline Billing History/": "billing_inflair_recon_report",
    "public/airline_files/GCG Invoice History/": "billing_promeus_invoice_report",
    "public/airline_files/FlightClassMapping/": "read_flight_class_mapping",
    "public/airline_files/FlightNumberMapping/": "read_flight_number_mapping",
}


def main(event, context):
    print("event object", event)

    if "detail" in event:
        key = event["detail"]["object"]["key"]
        bucket = event["detail"]["bucket"]["name"]
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Unsupported event format"}),
        }

    processor_function_name = None

    for prefix, processor in PREFIX_TO_PROCESSOR.items():
        if key.startswith(prefix):
            processor_function_name = processor
            break

    if not processor_function_name:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"No processor found for file: {key}"}),
        }

    reader_method_name = READER_FUNCTIONS.get(processor_function_name)
    if not reader_method_name:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"error": f"Unknown reader function: {processor_function_name}"}
            ),
        }

    print(
        f"Using processor: {processor_function_name}, " f"method: {reader_method_name}"
    )

    file, size = get_file_body_by_key(key, bucket)
    file_content = file.read()
    print(f"File size: {size} bytes")

    temp_dir = "/tmp"
    temp_file_path = os.path.join(temp_dir, f"temp_{os.path.basename(key)}")

    with open(temp_file_path, "wb") as temp_file:
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
            serialized_data = {class_name: items for class_name, items in data.items()}
            records_count = sum(len(items) for items in data.values())
        else:
            serialized_data = str(data)
            records_count = 0

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "File read successfully",
                    "processor_used": processor_function_name,
                    "data": serialized_data,
                    "records_count": records_count,
                },
                default=str,
            ),
        }
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        return {
            "statusCode": 500,
            "body": json.dumps(
                {"error": str(e), "processor_attempted": processor_function_name}
            ),
        }
