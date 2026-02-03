from django.shortcuts import render

# Create your views here.
# file_uploader/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from .utils import upload_to_minio
from .models import UploadedFile


class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]  # برای دریافت فایل

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=400)

        # ۱. آپلود در MinIO
        try:
            path = upload_to_minio(file_obj, request.user.id, file_obj.name)

            # ۲. ذخیره در دیتابیس خودمان
            uploaded_file = UploadedFile.objects.create(
                user=request.user,
                file_name=file_obj.name,
                minio_path=path,
                file_size=file_obj.size
            )

            return Response({
                "message": "File uploaded successfully",
                "file_id": uploaded_file.id,
                "path": path
            }, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=500)