# file_uploader/utils.py
import boto3
from django.conf import settings


def get_minio_client():
    config = settings.MINIO_STORAGE_CONFIG
    return boto3.client(
        's3',
        endpoint_url=config['ENDPOINT'],
        aws_access_key_id=config['ACCESS_KEY'],
        aws_secret_access_key=config['SECRET_KEY'],
        verify=False
    )


def upload_to_minio(file_obj, user_id, filename):
    s3 = get_minio_client()
    bucket_name = settings.MINIO_STORAGE_CONFIG['BUCKET_NAME']

    minio_path = f"user_{user_id}/{filename}"

    s3.upload_fileobj(file_obj, bucket_name, minio_path)
    return minio_path

