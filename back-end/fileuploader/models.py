
from django.db import models
from django.conf import settings

class UploadedFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='files')
    file_name = models.CharField(max_length=255)
    minio_path = models.TextField()
    file_size = models.BigIntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.phone} - {self.file_name}"