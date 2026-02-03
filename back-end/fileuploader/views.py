from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

# Create your views here.
# file_uploader/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .serializers import UploadedFileSerializer
from .utils import upload_to_minio, generate_download_url, delete_from_minio
from .models import UploadedFile

class FileListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get list of all files for the current user",
        responses={200: UploadedFileSerializer(many=True)},
        tags=['Files']
    )
    def get(self, request):
        files = UploadedFile.objects.filter(user=request.user)
        serializer = UploadedFileSerializer(files, many=True)
        return Response(serializer.data)

class FileDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a temporary download link for a specific file",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'url': openapi.Schema(type=openapi.TYPE_STRING)})},
        tags=['Files']
    )
    def get(self, request, file_id):
        try:
            file_obj = UploadedFile.objects.get(id=file_id, user=request.user)
            url = generate_download_url(file_obj.minio_path)
            return Response({"url": url})
        except UploadedFile.DoesNotExist:
            return Response({"error": "File not found"}, status=404)


# ۱. حذف فایل توسط مالک آن
class FileDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Delete a file from database and MinIO",
        responses={204: "Deleted Successfully", 404: "Not Found"},
        tags=['Files']
    )
    def delete(self, request, file_id):
        try:
            file_obj = UploadedFile.objects.get(id=file_id, user=request.user)

            # حذف از MinIO
            delete_from_minio(file_obj.minio_path)

            # حذف از دیتابیس
            file_obj.delete()

            return Response({"message": "فایل با موفقیت حذف شد"}, status=status.HTTP_204_NO_CONTENT)
        except UploadedFile.DoesNotExist:
            return Response({"error": "فایل پیدا نشد یا دسترسی ندارید"}, status=status.HTTP_404_NOT_FOUND)


# ۲. مشاهده تمام فایل‌های سیستم (مخصوص ادمین)
class AllFilesListView(APIView):
    permission_classes = [IsAdminUser]  # فقط کاربران is_staff یا superuser

    @swagger_auto_schema(
        operation_description="Admin only: Get list of ALL uploaded files across all users",
        responses={200: UploadedFileSerializer(many=True)},
        tags=['Admin Operations']
    )
    def get(self, request):
        files = UploadedFile.objects.all()
        # برای اینکه در لیست کل فایل‌ها بدانیم هر فایل مال کیست،
        # بهتر است یک سریالایزر مجزا بسازی که فیلد user.phone را هم نشان دهد
        serializer = UploadedFileSerializer(files, many=True)
        return Response(serializer.data)

    class FileUploadView(APIView):
        permission_classes = [IsAuthenticated]
        parser_classes = [MultiPartParser]

        @swagger_auto_schema(
            operation_description="Upload a file to MinIO",
            manual_parameters=[
                openapi.Parameter(
                    'file',
                    in_=openapi.IN_FORM,
                    type=openapi.TYPE_FILE,
                    required=True,
                    description="Selected file to upload"
                )
            ],
            responses={201: UploadedFileSerializer},
            tags=['Files']
        )
        def post(self, request):
            file_obj = request.FILES.get('file')
            if not file_obj:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # ۱. آپلود در MinIO
                path = upload_to_minio(file_obj, request.user.id, file_obj.name)

                # ۲. ذخیره در دیتابیس
                uploaded_file = UploadedFile.objects.create(
                    user=request.user,
                    file_name=file_obj.name,
                    minio_path=path,
                    file_size=file_obj.size
                )

                serializer = UploadedFileSerializer(uploaded_file)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Upload a file to MinIO",
        manual_parameters=[
            openapi.Parameter(
                'file',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="Selected file to upload"
            )
        ],
        responses={201: UploadedFileSerializer},
        tags=['Files']
    )
    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # ۱. آپلود در MinIO
            path = upload_to_minio(file_obj, request.user.id, file_obj.name)

            # ۲. ذخیره در دیتابیس
            uploaded_file = UploadedFile.objects.create(
                user=request.user,
                file_name=file_obj.name,
                minio_path=path,
                file_size=file_obj.size
            )

            serializer = UploadedFileSerializer(uploaded_file)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)