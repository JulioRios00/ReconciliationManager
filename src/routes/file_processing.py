from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
import boto3
import tempfile
import os
from src.database import get_db
from services.ccs_file_readers_db_service import (
    save_billing_inflair_to_db,
    save_billing_promeus_to_db,
    save_pricing_inflair_to_db,
    save_pricing_promeus_to_db
)

router = APIRouter()

## preciso criar lambda pois o serviço não roda diretamente no ec2
@router.post("/process-file")
async def process_s3_file(
    file_info: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Process a file that has been uploaded to S3

    Expected body:
    {
        "bucketName": "mtw-elementar-dev-018061303185",
        "objectKey": "airline_files/fileType/companyDetails-filename.xlsx",
        "fileType": "billing_inflair" | "billing_promeus" | "pricing_inflair" | "pricing_promeus"
    }
    """
    bucket_name = file_info.get("bucketName")
    object_key = file_info.get("objectKey")
    file_type = file_info.get("fileType")

    if not all([bucket_name, object_key, file_type]):
        raise HTTPException(
            status_code=400, 
            detail="Missing required fields: bucketName, objectKey, or fileType"
        )

    # Create a temporary file to store the downloaded S3 object
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")

    try:
        # Download the file from S3
        s3_client = boto3.client('s3')
        s3_client.download_file(bucket_name, object_key, temp_file.name)

        # Process the file based on its type
        if file_type == "billing_inflair":
            result = save_billing_inflair_to_db(temp_file.name, db)
            return {"message": f"Successfully processed {len(result)} billing inflair records"}

        elif file_type == "billing_promeus":
            result = save_billing_promeus_to_db(temp_file.name, db)
            return {"message": f"Successfully processed {len(result)} billing promeus records"}

        elif file_type == "pricing_inflair":
            result = save_pricing_inflair_to_db(temp_file.name, db)
            return {"message": f"Successfully processed {len(result)} pricing inflair records"}

        elif file_type == "pricing_promeus":
            result = save_pricing_promeus_to_db(temp_file.name, db)
            return {"message": "Successfully processed pricing promeus data for multiple flight classes"}

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_type}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing file: {str(e)}"
        )
    finally:
        # Clean up the temporary file
        os.unlink(temp_file.name)
