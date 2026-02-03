
# Register your models here.
from django.contrib import admin
from .models import UploadedFile

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'user', 'file_size', 'uploaded_at')
    list_filter = ('user', 'uploaded_at')
    search_fields = ('file_name', 'user__phone')
    readonly_fields = ('minio_path', 'uploaded_at')