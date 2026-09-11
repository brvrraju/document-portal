import os
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

def get_s3_client():
    return boto3.client('s3', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))

def get_dynamodb_resource():
    return boto3.resource('dynamodb', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))

def upload_to_s3(file_path: str, object_name: str) -> bool:
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        logger.warning("S3_BUCKET_NAME not set. Simulating upload for local dev.")
        return True
        
    s3_client = get_s3_client()
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
    except ClientError as e:
        logger.error(f"Failed to upload to S3: {e}")
        return False
    return True

def download_from_s3(object_name: str, file_path: str) -> bool:
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        logger.warning("S3_BUCKET_NAME not set. Simulating download for local dev.")
        # If it's local dev, the file should already be at file_path if generated locally.
        return os.path.exists(file_path)

    s3_client = get_s3_client()
    try:
        s3_client.download_file(bucket_name, object_name, file_path)
    except ClientError as e:
        logger.error(f"Failed to download from S3: {e}")
        return False
    return True

def upload_bytes_to_s3(file_bytes: bytes, object_name: str) -> bool:
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        logger.warning("S3_BUCKET_NAME not set. Simulating upload.")
        return True
    
    s3_client = get_s3_client()
    try:
        s3_client.put_object(Bucket=bucket_name, Key=object_name, Body=file_bytes)
    except ClientError as e:
        logger.error(f"Failed to upload bytes to S3: {e}")
        return False
    return True

def list_s3_prefix(prefix: str) -> list[str]:
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        logger.warning("S3_BUCKET_NAME not set. Simulating list.")
        return []
    
    s3_client = get_s3_client()
    try:
        resp = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' in resp:
            return [obj['Key'] for obj in resp['Contents']]
        return []
    except ClientError as e:
        logger.error(f"Failed to list S3 prefix: {e}")
        return []
