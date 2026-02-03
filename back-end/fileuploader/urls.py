from django.urls import path
from .views import (
    FileUploadView,
    FileListView,
    AllFilesListView,
    FileDownloadView,
    FileDeleteView
)

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('list/', FileListView.as_view(), name='file-list'),
    path('all-files/', AllFilesListView.as_view(), name='all-files-list'),
    path('download/<int:file_id>/', FileDownloadView.as_view(), name='file-download'),
    path('delete/<int:file_id>/', FileDeleteView.as_view(), name='file-delete'),
]