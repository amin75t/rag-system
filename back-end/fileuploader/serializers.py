from rest_framework import serializers

from fileuploader.models import UploadedFile
from fileuploader.utils import generate_download_url

class UploadedFileSerializer(serializers.ModelSerializer):
    user_phone = serializers.ReadOnlyField(source='user.phone') # نمایش شماره کاربر
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedFile
        fields = ['id', 'user_phone', 'file_name', 'file_size', 'download_url', 'uploaded_at']
    def get_download_url(self, obj):
        return generate_download_url(obj.minio_path)