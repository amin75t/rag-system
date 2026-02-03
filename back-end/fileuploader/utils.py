# file_uploader/utils.py
import boto3
from django.conf import settings
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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


def generate_download_url(minio_path, expiration=3600):
    s3 = boto3.client(
        's3',
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
    )

    url = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': settings.MINIO_BUCKET_NAME,
            'Key': minio_path
        },
        ExpiresIn=expiration
    )
    return url
def delete_from_minio(minio_path):
    s3 = boto3.client(
        's3',
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
    )
    s3.delete_object(Bucket=settings.MINIO_BUCKET_NAME, Key=minio_path)